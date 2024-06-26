# coding: utf-8

import os.path as osp
import pandas as pd

from ddf_utils.io import open_google_spreadsheet, serve_datapoint


DOCID = '1I-E4T06MhZMgU_yN-sT4D2Kq-jfquBTQjgxE2a-9TAU'
SHEET = 'Output_By_Decile'

DIMENSIONS = ['geo', 'time', 'decile']
OUT_DIR = '../../'

COLUMN_TO_CONCEPT = {'CO2e per capita': 'co2e_per_cap','Total Emissions tCO2':'total_co2','Mean income':'mean_income'}


def gen_datapoints(df_: pd.DataFrame):
    df = df_.copy()
    df = df.set_index(DIMENSIONS).drop('name', axis=1)  # set index and drop column 'name'
    for c in df:
        yield (c, df[[c]])


def create_geo_domain(df: pd.DataFrame) -> pd.DataFrame:
    return df[['geo', 'name']].drop_duplicates()


def main():
    print('running etl...')
    data = pd.read_excel(open_google_spreadsheet(DOCID), sheet_name=SHEET)

    measures = list()

    for c, df in gen_datapoints(data):
        c_id = COLUMN_TO_CONCEPT[c]
        df.columns = [c_id]
        serve_datapoint(df, OUT_DIR, c_id)

        measures.append((c_id, c))

    measures_df = pd.DataFrame(measures, columns=['concept', 'name'])
    measures_df['concept_type'] = 'measure'
    measures_df['domain'] = ''

    discrete_df = pd.DataFrame.from_dict(
        dict(concept=['geo', 'name', 'time','decile','domain'],
             name=['Geo', 'Name', 'Time','Decile','Domain'],
             concept_type=['entity_domain', 'string', 'time','entity_domain', 'string'])
    )
    pd.concat([measures_df, discrete_df], ignore_index=True).to_csv(osp.join(OUT_DIR, 'ddf--concepts.csv'), index=False)

    geo_df = create_geo_domain(data)

    # Inserting missing geos for compatibility with other datasets
    missing_geos = pd.DataFrame({'geo':['hos','mco','smr'],'name':['Holy See','Macao','San Marino']})
    geo_df = pd.concat([geo_df, missing_geos], ignore_index=True)

    geo_df.to_csv(osp.join(OUT_DIR, 'ddf--entities--geo.csv'), index=False)


if __name__ == '__main__':
    main()
    print('Done.')
