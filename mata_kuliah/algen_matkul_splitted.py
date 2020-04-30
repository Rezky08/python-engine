import copy
import numpy as np
import time
import random
import math
from mata_kuliah.algen_matkul import algen_matkul
import sys
import threading
import queue


class algen_matkul_splitted():
    def __init__(self, nn_params: dict, num_generation: int, num_population: int,
                 crossover_rate: float, mutation_rate: float, timeout=0, threading=True):

        self.nn_params = nn_params
        self.num_population = num_population
        self.num_generation = num_generation+1
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.timeout = timeout
        self.threading = threading
        self.nn_params_hari = {x: {} for x in self.nn_params['hari']}

    def splitting(self):
        chromosom_cp = copy.deepcopy(self.nn_params['mata_kuliah'])
        mata_kuliah_split = {x: [] for x in self.nn_params['hari']}
        while(len(chromosom_cp) != 0):
            hari_select = random.choice(self.nn_params['hari'])
            rn = random.random() * len(chromosom_cp)
            rn = math.floor(rn)
            mata_kuliah_split[hari_select].append(chromosom_cp[rn])
            chromosom_cp.pop(rn)

        for index, item in enumerate(self.nn_params['hari']):
            nn_params = copy.deepcopy(self.nn_params)
            ruang_waktu_filtered = filter(
                lambda x: x['hari'] == item, self.nn_params['ruang_waktu'])
            ruang_waktu_simple_filtered = filter(
                lambda x: x['hari'] == index, self.nn_params['ruang_waktu_simple'])
            nn_params['mata_kuliah'] = mata_kuliah_split[item]
            nn_params['ruang_waktu'] = list(ruang_waktu_filtered)
            nn_params['ruang_waktu_simple'] = list(ruang_waktu_simple_filtered)
            self.nn_params_hari[item] = copy.deepcopy(nn_params)

    def algen_threading(self, nn_params, que=None, threading=False):
        algen = algen_matkul(nn_params, self.num_generation, self.num_population, self.crossover_rate,
                             self.mutation_rate, self.timeout, threading)
        while (True):
            print(nn_params['ruang_waktu'][0]['hari'])
            result, fitscore, elapsed_time = algen.run_generation()
            if fitscore == 1:
                break
        print("{} Selesai".format(nn_params['ruang_waktu'][0]['hari']))

        if que != None:
            que.put(result)
        return result

    def run_generation(self):
        self.splitting()
        result_chromosom = []
        if self.threading:
            q = []
            th = []
            for item in self.nn_params_hari:
                q.append(queue.Queue())
                th.append(threading.Thread(target=self.algen_threading,
                                           args=[self.nn_params_hari[item], q[-1], True]))
                th[-1].start()
            for item in th:
                item.join()
            for item in q:
                result_chromosom += item.get()
        else:
            for item in self.nn_params_hari:
                print(item)
                result = self.algen_threading(
                    self.nn_params_hari[item], threading=True)
                result_chromosom += result
        return result_chromosom
