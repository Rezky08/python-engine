import copy
import numpy as np
import time
import random
import math
from mata_kuliah.step1.algen_matkul_new import algen_matkul
import sys
import threading
import queue
import datetime


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
        self.nn_params_batch = []

    def splitting(self):
        chromosom_cp = copy.deepcopy(self.nn_params['mata_kuliah'])
        kode_dosen = map(lambda x:x['kode_dosen'],chromosom_cp)
        kode_dosen = list(kode_dosen)
        kode_dosen = np.unique(kode_dosen)
        mata_kuliah_split = {}
        for item in kode_dosen:
            mata_kuliah_split[item] = filter(lambda x:x['kode_dosen']==item ,chromosom_cp)
            mata_kuliah_split[item] = list(mata_kuliah_split[item])
        batch = []
        batch_item = []
        kode_dosen_cp = copy.deepcopy(kode_dosen)
        kode_dosen_cp = list(kode_dosen_cp)
        while len(kode_dosen_cp)>0:
            choosed = random.random() * len(kode_dosen_cp)
            choosed = math.floor(choosed)
            batch_item.append(kode_dosen_cp[choosed])
            kode_dosen_cp.pop(choosed)
            if len(batch_item)>=10:
                batch.append(batch_item)
                batch_item = []
        self.nn_params_batch = [copy.deepcopy(self.nn_params) for i in batch]

        for index,item in enumerate(batch):
            batch_item = []
            for index_item, item_item in enumerate(item):
                batch_item += mata_kuliah_split[item_item]
            batch[index] = copy.deepcopy(batch_item)
            self.nn_params_batch[index]['mata_kuliah'] = copy.deepcopy(batch[index])

    def algen_threading(self, nn_params, que=None, threading=False):
        algen = algen_matkul(nn_params, self.num_generation, self.num_population, self.crossover_rate,
                             self.mutation_rate, self.timeout, threading)
        # result, fitscore, elapsed_time = algen.run_generation()
        # fit_score_res = []
        while (True):
            print("Mulai {}".format(datetime.datetime.now()))
            result, fitscore, elapsed_time = algen.run_generation()
            # fit_score_res.append(fitscore)
            # print("result fit score : {}".format(fit_score_res[-5:]))
            # fit_score_unique = np.unique(fit_score_res[-5:])
            # print("result fit unique score : {}".format(fit_score_unique))
            # if len(fit_score_res)>=5:
            #     break
            if fitscore == 1:
                break
        print("Selesai {}".format(datetime.datetime.now()))

        if que != None:
            que.put(result)
        return result

    def run_generation(self):
        self.splitting()
        result_chromosom = []
        if self.threading:
            q = []
            th = []
            for index,item in enumerate(self.nn_params_batch):
                q.append(queue.Queue())
                th.append(threading.Thread(target=self.algen_threading,
                                           args=[self.nn_params_batch[index], q[-1], True]))
                th[-1].start()
            for item in th:
                item.join()
            for item in q:
                result_chromosom += item.get()
        else:
            for index,item in enumerate(self.nn_params_batch):
                result = self.algen_threading(
                    self.nn_params_batch[index], threading=True)
                result_chromosom += result
        self.nn_params['mata_kuliah'] = result_chromosom
        print(len(self.nn_params['mata_kuliah']))
        algen = algen_matkul_next(self.nn_params,self.num_generation,self.num_population,self.crossover_rate,self.mutation_rate,self.timeout,True)
        print("\n"*3)
        print("======== Algen Next Start ========")
        time.sleep(5)
        result_chromosom,fit_score,elapsed_time = algen.run_generation()
        return result_chromosom
