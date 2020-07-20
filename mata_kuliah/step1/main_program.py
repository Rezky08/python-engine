from mata_kuliah.step1.algen_matkul_new import algen_matkul
from mata_kuliah.step1.algen_matkul_splitted_new import algen_matkul_splitted
import pandas as pd
import  numpy as np
from datetime import datetime
import  copy
import json
import sys

file = open('params.json',)
params = json.load(file)
# rules = self.requests['rules']
nn_params = params['nn_params']

# sesi sorted
for sesi_item in nn_params['sesi']:
    for sesi_in_item in sesi_item.keys():
        sesi_item[sesi_in_item] = datetime.strptime(
            sesi_item[sesi_in_item], "%X").time()

nn_params['sesi'] = sorted(
    nn_params['sesi'], key=lambda x: x['sesi_mulai'])

ruang_waktu = []
ruang_waktu_simple = []

for ruang_index, ruang_item in enumerate(nn_params['ruang']):
    for hari_index, hari_item in enumerate(nn_params['hari']):
        for sesi_index, sesi_item in enumerate(nn_params['sesi']):
            combine = {
                'ruang': ruang_item,
                'hari': hari_item,
                'sesi': sesi_item
            }
            ruang_waktu.append(combine)
            combine = {
                'ruang': ruang_index,
                'hari': hari_index,
                'sesi': sesi_index
            }
            ruang_waktu_simple.append(combine)

nn_params['ruang_waktu'] = ruang_waktu
nn_params['ruang_waktu_simple'] = ruang_waktu_simple
num_generation = params['num_generation']
num_population = params['num_population']
crossover_rate = params['crossover_rate']
mutation_rate = params['mutation_rate']
timeout = params['timeout']

algen = algen_matkul(nn_params,num_generation,num_population,crossover_rate,mutation_rate)
res,fit_score,time_elapsed = algen.run_generation()
print(len(res))
print(np.asarray(res))