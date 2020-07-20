import json
import pandas as pd
import numpy as np
from dosen.pembagi_kelompok import pembagi_kelompok
from dosen.algen_only_dosen import algen_only_dosen
from mata_kuliah.step1.algen_matkul_new import algen_matkul as algen_matkul_step1
from mata_kuliah.step2.algen_matkul_new import algen_matkul as algen_matkul_step2
from mata_kuliah.step3.algen_matkul_new import algen_matkul as algen_matkul_step3
import sys
from datetime import datetime


class handle:
    def __init__(self, requests: dict):
        self.requests = requests

    def response(self):
        pass

    def kelompok(self):
        # get kelompok of matkul
        peminat_params = self.requests['peminat_params']
        peminat_props = self.requests['peminat_props']
        bagi_kelompok = pembagi_kelompok(peminat_params, peminat_props)
        bagi_kelompok = bagi_kelompok.bagi_kelompok()

        # get dosen by matkul

        return bagi_kelompok

    def dosen(self):
        nn_params = {
            'matkul_dosen': pd.DataFrame(self.requests['nn_params']['matkul_dosen']).to_dict(orient='list'),
        }
        try:
            nn_params['mata_kuliah'] = self.requests['nn_params']['mata_kuliah']
        except:
            nn_params['mata_kuliah'] = self.kelompok()

        rules = self.requests['rules']
        num_generation = self.requests['num_generation']
        num_population = self.requests['num_population']
        crossover_rate = self.requests['crossover_rate']
        mutation_rate = self.requests['mutation_rate']
        timeout = self.requests['timeout']

        algen = algen_only_dosen(nn_params, rules, num_generation,
                                 num_population, crossover_rate, mutation_rate, timeout)
        max_chromosom, fit_score, running_time = algen.run_generation()
        results = []
        result = {
            'data': max_chromosom,
            'fit_score': fit_score
        }
        return result

    def jadwal(self):
        # rules = self.requests['rules']
        nn_params = self.requests['nn_params']

        # sesi sorted
        for sesi_item in self.requests['nn_params']['sesi']:
            for sesi_in_item in sesi_item.keys():
                sesi_item[sesi_in_item] = datetime.strptime(
                    sesi_item[sesi_in_item], "%X").time()

        self.requests['nn_params']['sesi'] = sorted(
            self.requests['nn_params']['sesi'], key=lambda x: x['sesi_mulai'])

        ruang_waktu = []
        ruang_waktu_simple = []

        for ruang_index, ruang_item in enumerate(self.requests['nn_params']['ruang']):
            for hari_index, hari_item in enumerate(self.requests['nn_params']['hari']):
                for sesi_index, sesi_item in enumerate(self.requests['nn_params']['sesi']):
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
        num_generation = self.requests['num_generation']
        num_population = self.requests['num_population']
        crossover_rate = self.requests['crossover_rate']
        mutation_rate = self.requests['mutation_rate']
        timeout = self.requests['timeout']

        print("=========== STEP 1 ================")
        algen_step1 = algen_matkul_step1(nn_params, num_generation, num_population, crossover_rate, mutation_rate)
        res, fit_score, time_elapsed = algen_step1.run_generation()
        nn_params['mata_kuliah'] = res
        print("=========== STEP 2 ================")
        algen_step2 = algen_matkul_step2(nn_params, num_generation, num_population, crossover_rate, mutation_rate)
        res, fit_score, time_elapsed = algen_step2.run_generation()
        nn_params['mata_kuliah'] = res
        print("=========== STEP 3 ================")
        algen_step3 = algen_matkul_step3(nn_params, num_generation, num_population, crossover_rate, mutation_rate)
        res, fit_score, time_elapsed = algen_step3.run_generation()

        result = {
            'data': res,
            'fit_score': fit_score
        }
        return result

    def dosen_dummy(self):
        nn_params = {
            'mata_kuliah': self.requests['nn_params']['mata_kuliah'],
            'matkul_dosen': self.requests['nn_params']['matkul_dosen']
        }

        rules = self.requests['rules']
        num_generation = self.requests['num_generation']
        num_population = self.requests['num_population']
        crossover_rate = self.requests['crossover_rate']
        mutation_rate = self.requests['mutation_rate']
        timeout = self.requests['timeout']

        dummy = pd.read_csv('dosen/result/result_1.0.csv', index_col=0)
        dummy_dict = dummy.to_dict(orient='record')
        results = []
        for index in range(3):
            result = {
                'data': dummy_dict,
                'fit_score': 1
            }
            results.append(result)
        return results
