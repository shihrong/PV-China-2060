# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import pvlib
import h5py
import xarray as xr
import code

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------
# Function.
def Potential_Power(times, GHI, latitude, longitude, altitude, t2m, Wind_Speed):
    """
    Effective irradiance is total plane of array (POA) irradiance adjusted for
    angle of incidence losses, soiling, and spectral mismatch.

    Surface tilt(Panel tilt from horizontal) is equal to latitude, and surface azimuth is south-facing.

    Solar position model is NREL SPA, separation model is DISC model, transposition model is Perez model, reflection Loss model is Xie model,
    spectral Loss model is SAPM model, and soiling loss sets 1.5%.

    Solar panel module is "Canadian_Solar_CS5P_220M___2009_", the refraction index of the PV module cover material (npv=1.526) for normal,
    and the refraction index of the pyranometer cover, which is usually a fused silica dome (nt=1.4585).

    Parameters
    ----------
    GHI: dataframe.
        Global horizontal irradiance in W/m^2.
    latitude: float.
        Positive is north of the equator.
        Use decimal degrees notation.
    longitude: float.
        Positive is east of the prime meridian.
        Use decimal degrees natation.
    altitude: float.
        Altitude from sea level in meters.

    Returns
    ----------
    Ee: numeric
        Effective irradiance.
    """
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # latitude, longitude
    lat = latitude
    lon = longitude
    # altitude
    elevation = altitude
    # GHI

    # time zone
    time_zone = 'UTC'
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Solar Position model
    # spa_python: the solar positionig algorithm (SPA) is commonly regarded as the most accurate one to date.
    # Outputs: apparent_zenith (degrees), zenith (degrees), apparent_elevation (degrees), elevation (degrees), azimuth (degrees), equation_of_time (minutes).
    position = pvlib.solarposition.spa_python(time=times,
                                              latitude=lat,
                                              longitude=lon,
                                              altitude=elevation)
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # the angle of incidence of the solar vector on a surface. This is the angle between the solar vector and the surface normal.
    # Input all angles in degrees.
    aoi = pvlib.irradiance.aoi(surface_tilt=lat,
                               surface_azimuth=180,
                               solar_zenith=position.apparent_zenith,
                               solar_azimuth=position.azimuth)
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Separation model: DISC model (Direct Insolation Simulation Code)
    # Estimate Direct Normal Irradiance from Global Horizontal Irradiance using the DISC model.
    # The modeled direct normal irradiance in W/m^2
    disc = pvlib.irradiance.disc(ghi=GHI,
                                 solar_zenith=position.apparent_zenith,
                                 datetime_or_doy=times)
    dni = disc.dni
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Diffuse horizontal irradiance. [W/m2]
    # DHI = GHI - DNI cosZ, where Z is the zenith angle.
    zenith = position.apparent_zenith
    dhi = GHI - np.cos(zenith / 180 * np.pi) * dni
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Determine extraterrestrial radiation from day of year.
    dni_extra = pvlib.irradiance.get_extra_radiation(datetime_or_doy=times,
                                                     method='nrel',
                                                     epoch_year=2018)
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Transposition model
    # Determine total in-plane irradiance and its beam, sky diffuse and ground reflected components, using the perez model.
    # I_{tot} = I_{beam} + I_{skydiffuse} + I_{ground}
    transposition_irradiance = pvlib.irradiance.get_total_irradiance(surface_tilt=lat,
                                                                     surface_azimuth=180,
                                                                     solar_zenith=position.apparent_zenith,
                                                                     solar_azimuth=position.azimuth,
                                                                     dni=dni,
                                                                     ghi=GHI,
                                                                     dhi=dhi,
                                                                     dni_extra=dni_extra,
                                                                     model='perez')
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Reflection Loss model
    # Fresnel:
    # refraction index of the PV module cover material, npv=1.526 for normal, npv=1.3 for anti-reflection coated glass.
    npv = 1.526
    theta_RefractiveAngle = (np.arcsin(np.sin(aoi / 180 * np.pi) / npv)) / np.pi * 180

    Rd = (np.sin((theta_RefractiveAngle - aoi) / 180 * np.pi)) ** 2 / (
        np.sin((theta_RefractiveAngle + aoi) / 180 * np.pi)) ** 2 + \
         (np.tan((theta_RefractiveAngle - aoi) / 180 * np.pi)) ** 2 / (
             np.tan((theta_RefractiveAngle + aoi) / 180 * np.pi)) ** 2

    R0 = ((npv - 1) / (npv + 1)) ** 2
    # the physical relative transmittance for beam radiation (tau_b) is only based on Fresnel equations:
    tau_b = (1 - Rd / 2) / (1 - R0)

    # tau_b using pvlib
    # tau_b_pvlib = pvlib.iam.physical(aoi=aoi)
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Xie:
    nt = 1.4585  # the refeaction index of the pyranometer cover, which is usually a fused silica dome with nt=1.4585
    tilt_angle = lat  # tilt angle
    S = tilt_angle / 180 * np.pi  # radians
    w = (npv * (nt + 1) ** 2) / (nt * (npv + 1) ** 2) * (
                2.77526E-9 + 3.74953 * npv - 5.18727 * (npv) ** 2 + 3.41186 * (npv) ** 3 - 1.08794 * (
            npv) ** 4 + 0.13606 * (npv) ** 5)
    # the relative transmittance for diffuse radiation (tau_d):
    tau_d = 2 * w / (np.pi * (1 + np.cos(S))) * \
            (30 / 7 * np.pi - 160 / 21 * S - 10 / 3 * np.pi * np.cos(S) + 160 / 21 * np.cos(S) * np.sin(S) - \
             5 / 3 * np.pi * np.cos(S) * (np.sin(S)) ** 2 + 20 / 7 * np.cos(S) * (np.sin(S)) ** 3 - 5 / 16 * np.pi * (
                 np.sin(S)) ** 4 + 16 / 105 * np.cos(S) * (np.sin(S)) ** 5)

    # the relative transmittance for ground-reflected radiation (tau_g):
    tau_g = 40 * w / (21 * (1 - np.cos(S))) - tau_d * (1 + np.cos(S)) / (1 - np.cos(S))
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # absorbed radiation (G'c):
    # G'_c = tau_b*B_c + tau_d*D_c + tau_g*D_g
    absorbed_radiation = tau_b * transposition_irradiance.poa_direct + tau_d * transposition_irradiance.poa_sky_diffuse + tau_g * transposition_irradiance.poa_ground_diffuse
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Spectral Loss model
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
    # Calculate relative (not pressure-adjusted) airmass at sea level.(model='kastenyoung1989')
    airmass_relative = pvlib.atmosphere.get_relative_airmass(zenith=position.apparent_zenith)
    # Determine absolute (pressure-adjusted) airmass from relative airmass and pressure.
    airmass_absolute = pvlib.atmosphere.get_absolute_airmass(airmass_relative=airmass_relative)
    # Calculates the SAPM spectral loss coefficient, F1.
    F1 = pvlib.pvsystem.sapm_spectral_loss(airmass_absolute=airmass_absolute, module=module)
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Soil loss 1.5%
    SF = 0.985
    # effective irradiance (Ee):
    Ee = F1 * absorbed_radiation * SF

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # 电池温度
    #t2m unit: ℃
    cell_temperature = pvlib.temperature.sapm_cell(Ee,
                                                   temp_air=t2m,
                                                   wind_speed=Wind_Speed,
                                                   a=-2.98, b=-0.0471, deltaT=1, irrad_ref=1000.0)

    # --------- PVWatts
    PVWatts_DC = pvlib.pvsystem.pvwatts_dc(Ee, cell_temperature, pdc0=1000, gamma_pdc=-0.00408, temp_ref=25.0)

    return PVWatts_DC

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------


month = ['01','04','07','10']

year = '2060'
path = ['_cs_','_hb_','_hr_','_bs_']

for k,ip in enumerate(path):
    for im in range(len(month)):
        if month[im] =='01':
            times = pd.date_range(start='2060-01-01 00:00:00', end='2060-01-31 23:00:00', freq='1h', tz='UTC')
        if month[im] =='04':
            times = pd.date_range(start='2060-04-01 00:00:00', end='2060-04-30 23:00:00', freq='1h', tz='UTC')
        if month[im] == '07':
            times = pd.date_range(start='2060-07-01 00:00:00', end='2060-07-31 23:00:00', freq='1h', tz='UTC')
        if month[im] =='10':
            times = pd.date_range(start='2060-10-01 00:00:00', end='2060-10-31 23:00:00', freq='1h', tz='UTC')

        data = xr.open_dataset('../wrfout/2060/output_' + year +month[im] + ip+'.nc')
        # code.interact(local=locals())
        XLAT = data.XLAT.values
        XLON = data.XLONG.values
        XTIME = data.XTIME.values
        data = xr.open_dataset('../wrfout/2060/output_' + year +month[im] + ip+'.nc',decode_times=False)
        SWDOWN = data.SWDOWN.values
        # code.interact(local=locals())

        data = xr.open_dataset('../wrfout/2060/output_' + year +month[im]+ ip +'.nc',decode_times=False)
        T2 = data.T2.values-273.15
        data = xr.open_dataset('../wrfout/2060/output_' + year +month[im]+ ip +'.nc',decode_times=False)
        u10 = data.U10.values
        v10 = data.V10.values
        WindSpeed = np.sqrt(u10 ** 2 + v10 ** 2)
        data = xr.open_dataset('../wrfout/2060/HGT.nc')
        HGT = data.HGT.values
        # code.interact(local=locals())

        # loop for every pixels
        dim = SWDOWN.shape
        PV_Potential_Power = np.full(dim,np.nan)
        # code.interact(local=locals())

        for i in range(dim[1]):
            for j in range(dim[2]):
                PV_Potential_Power[:,i,j] = Potential_Power(times= times, GHI=SWDOWN[:,i,j], latitude=XLAT[i,j], longitude=XLON[i,j], altitude=HGT[0:dim[0],i,j], t2m=T2[:,i,j], Wind_Speed=WindSpeed[:,i,j])

        
        del dim
        # write PV power into hdf file
        f1 = h5py.File('../wrfout/2060/PV'+ip+ '_'+year +month[im]+ '.hdf', "w")
        f1.create_dataset('PV_PP', np.shape(PV_Potential_Power), dtype='float32', data=PV_Potential_Power)
        f1.close()
        # del PV_Potential_Power






