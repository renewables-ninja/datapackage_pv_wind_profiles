import os
import json
import yaml


country_map = {
    'BE': 'Belgium',
    'BG': 'Bulgaria',
    'CZ': 'Czech Republic',
    'DK': 'Denmark',
    'DE': 'Germany',
    'EE': 'Estonia',
    'IE': 'Ireland',
    'GR': 'Greece',
    'ES': 'Spain',
    'FR': 'France',
    'IT': 'Italy',
    'CY': 'Cyprus',
    'LV': 'Latvia',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'HU': 'Hungary',
    'MT': 'Malta',
    'NL': 'Netherlands',
    'AT': 'Austria',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'SI': 'Slovenia',
    'SK': 'Slovakia',
    'FI': 'Finland',
    'SE': 'Sweden',
    'GB': 'Great Britain',
    'CH': 'Switzerland',
    'GR': 'Greece',
    'NO': 'Norway',
    'ME': 'Montenegro',
    'MD': 'Moldova',
    'RS': 'Serbia',
    'HR': 'Croatia',
    'AL': 'Albania',
    'MK': 'Macedonia',
    'BA': 'Bosnia and Herzegovina',
}


metadata_head = '''
hide: 'yes'
name: ninja_pv_wind_profiles
title: Renewables.ninja PV and Wind Profiles
description: Simulated hourly country-aggregated PV and wind capacity factors for Europe
long_description: 'This data package contains simulated wind and PV capacity factors from Renewables.ninja, at hourly resolution, for all European countries. Unlike the time series data package, which contains data reported from network operators, this package contains simulated data using historical weather conditions.\n\n -- License: Creative Commons Attribution-NonCommercial 4.0, https://creativecommons.org/licenses/by-nc/4.0/.\n\n-- More information and references to cite when using these data: https://doi.org/10.1016/j.energy.2016.08.060 and https://doi.org/10.1016/j.energy.2016.08.068\n\n-- The data are generated using the MERRA-2 reanalysis, for current PV and Wind capacities in Europe. For more data, e.g. PV simulations based on the SARAH dataset and future wind capacity factors, see https://www.renewables.ninja/#/country'
documentation: 'https://github.com/renewables-ninja/datapackage_pv_wind_profiles/blob/{version}/main.ipynb'
version: '{version}'
last_changes: '{changes}'
keywords:
  - time series
  - power systems
  - renewables
  - wind
  - solar
  - pv
geographical-scope: 36 European countries
contributors:
  - web: https://www.renewables.ninja/
    name: Stefan Pfenninger
    email: stefan.pfenninger@usys.ethz.ch
licenses:
  - url: https://creativecommons.org/licenses/by-nc/4.0/
    name: Creative Commons Attribution-NonCommercial
    version: 4.0
    id: cc-by-nc-4.0
sources:
  - name: Renewables.ninja
    web: https://www.renewables.ninja/#/country
resources:
  # - mediatype: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
  #   format: xlsx
  #   path: ninja_pv_wind_profiles.xlsx
  - mediatype: text/csv
    format: csv
    path: ninja_pv_wind_profiles_singleindex.csv
    encoding: UTF8
    schema:
      primaryKey: time
      missingValue: ""
      fields:
        - name: time
          description: Start of time period in Coordinated Universal Time
          type: datetime
          format: fmt:%Y-%m-%dT%H%M%SZ
          opsd-contentfilter: true
    dialect:
        csvddfVersion: 1.0
        delimiter: ","
        lineTerminator: "\\n"
        header: true
    alternative_formats:
        - path: ninja_pv_wind_profiles_singleindex.csv
          stacking: Singleindex
          format: csv
        # - path: ninja_pv_wind_profiles.xlsx
        #   stacking: Multiindex
        #   format: xlsx
        - path: ninja_pv_wind_profiles_multiindex.csv
          stacking: Multiindex
          format: csv
        # - path: ninja_pv_wind_profiles_stacked.csv
        #   stacking: Stacked
        #   format: csv
'''


def get_description(kind, tech, geo, scenario):
    # FIXME: ugly hack!
    scenario = scenario.replace('termfuture', 'term future')
    kinds = {
        'national': 'Nationally-aggregated {scenario} {tech} generation capacity factor in {geo}',
        'offshore': 'Offshore {scenario} {tech} generation capacity factor in {geo}',
        'onshore': 'Onshore {scenario} {tech} generation capacity factor in {geo}',
    }
    return kinds[kind].format(tech=tech, geo=geo, scenario=scenario)


def get_field(col):
    # col = ('AL', 'pv', 'merra-2', 'current', 'national')
    # iso, tech, dataset, run, variable = col
    iso, tech, variable, run  = col

    country_name = country_map[iso]

    field_template = '''
    name: {region}_{variable}_{attribute}
    description:
    type: number (float)
    opsd-properties:
        Region: "{region}"
        Variable: {variable}
        Attribute: {attribute}
    '''.format(region=iso, variable=tech + '_' + variable, attribute=run)

    field = yaml.load(field_template)
    field['description'] = get_description(variable, tech, country_name, run)

    return field


def generate_json(df, version, changes):
    '''
    Creates a datapackage.json file that complies with the Frictionless
    data JSON Table Schema from the information in the column MultiIndex.

    Parameters
    ----------
    df: pandas.DataFrame
        A dict with keys '15min' and '60min' and values the respective
        DataFrames
    version: str
        Version tag of the Data Package
    changes : str
        Desription of the changes from the last version to this one.

    Returns
    ----------
    None

    '''
    metadata = yaml.load(metadata_head.format(version=version, changes=changes))

    fields = [get_field(col) for col in df.columns]

    # FIXME: very ugly hack to get fields into the right place in the
    # metadata_head template
    existing_fields = metadata['resources'][0]['schema']['fields']
    metadata['resources'][0]['schema']['fields'] = existing_fields + fields

    out_path = os.path.join(version, 'datapackage.json')
    os.makedirs(version, exist_ok=True)

    datapackage_json = json.dumps(metadata, indent=4, separators=(',', ': '))
    with open(out_path, 'w') as f:
        f.write(datapackage_json)
