import pandas as pd
import json


class sample:
    def __init__(self, samplesheet, n):
        self.samplesheet = samplesheet
        self.n = n

    def sampleprop(self):
        df_static = pd.read_excel(self.samplesheet, str(self.n), None)
        df_dyn = pd.read_excel(self.samplesheet, str(self.n), skiprows=7)
        client = df_static.iloc[0][1]
        sid = df_static.iloc[1][1]
        length = df_static.iloc[2][1]
        diameter = df_static.iloc[3][1]
        vessel = df_static.iloc[4][1]
        comment = df_static.iloc[5][1]
        fluid = df_static.iloc[0][4]
        temperature = df_static.iloc[1][4]
        perm_min = df_static.iloc[2][4]
        perm_max = df_static.iloc[3][4]
        time_scale = df_static.iloc[4][4]
        visc_mult = df_static.iloc[5][4]
        time_start = df_dyn['Time Start'].to_list()
        time_end = df_dyn['Time End'].to_list()
        pump = df_dyn['Pump'].to_list()
        instance_comment = df_dyn['Comments'].to_list()
        pconf = df_dyn['Pconf'].to_list()
        sampledict = {'client': client, 'sample ID': sid, 'length':length, 'diameter':diameter, 'vessel': vessel,
        'comment': comment, 'fluid': fluid, 'temperature': temperature, 'perm_min': perm_min, 'perm_max': perm_max,
        'time scale': time_scale, 'Start Time': time_start, 'End Time': time_end, 'Pump': pump, 
        'Instance Comment': instance_comment, 'Confining Pressure': pconf, 'visc_mult': visc_mult}
        return sampledict

# samplesheet = r"M:\Team Chaos Liquid Perm Initialization v5.xlsx"

# sample_1 = sample(samplesheet, 1)
# sample_2 = sample(samplesheet, 2)
# sample_3 = sample(samplesheet, 3)
# sample_4 = sample(samplesheet, 4)
# sample_5 = sample(samplesheet, 5)
# print(type(sample_1.sampleprop()))

# samplelist = [sample_1, sample_2, sample_3, sample_4, sample_5]

# for i in samplelist:
#     sampleid = r"C:\Users\Brian.Chin\Documents\lpermplotter\json output\\" + i.sampleprop()['client'] + " "+ i.sampleprop()['sample ID'] + ".json"
#     with open(sampleid, "w") as f:
#         json.dump(i.sampleprop(), f, default=str, indent=4, sort_keys=True)

# print(sample_1.sampleprop()['client'])
