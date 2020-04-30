import numpy as np
import pandas as pd
import math
import sys
import copy
import  time
import queue
import threading
class rules():
    def __init__(self,nn_params):
        self.nn_params = nn_params
        self.penalty = {
            'dosen_ruang_waktu' : 1,
            'sks':1
        }

    def check_sks(self,chromosom):
        sks_score = 0
        chromosom_translate = np.array(self.nn_params['ruang_waktu_simple'])[chromosom]
        chromosom_translate_values = [list(x.values()) for x in chromosom_translate]
        chromosom_translate_values_new = []

        for index, item in enumerate(chromosom_translate_values):
            sks_matkul = self.nn_params['mata_kuliah'][index]['sks_matkul']
            if item[2]+sks_matkul-1 > len(self.nn_params['sesi']):
                sks_score+=1
                continue

            for i in range(sks_matkul):
                item_temp = copy.deepcopy(item)
                item_temp[2]+=i
                chromosom_translate_values_new.append(item_temp)


        chromosom_unique,chromosom_unique_count = np.unique(chromosom_translate_values_new,axis=0,return_counts=True)
        fails = np.where(chromosom_unique_count>1)
        fails = chromosom_unique_count[fails]
        fails = len(fails)
        sks_score+=fails
        return sks_score

    def check_dosen_ruang_waktu(self,chromosom):
        dosen_ruang_waktu_score = 0
        kode_dosen = map(lambda x:x['kode_dosen'],self.nn_params['mata_kuliah'])
        kode_dosen_ruang_waktu = []

        for index,item in enumerate(kode_dosen):
            kode_dosen_ruang_waktu.append(tuple([item,chromosom[index]]))
        kode_dosen_ruang_waktu_unique,kode_dosen_ruang_waktu_counts = np.unique(kode_dosen_ruang_waktu,return_counts=True,axis=0)
        fails = np.where(kode_dosen_ruang_waktu_counts>1)
        dosen_ruang_waktu_score = len(fails[0])
        return  dosen_ruang_waktu_score

    def calculate_chromosom(self,chromosom):
        """
        formulas = 1 / (1+(penalty1 * num_penalty1)+...+(penaltyn * num_penaltyn))
        :return:
        """

        num_penalty = {}
        sum_penalty = 0

        for k in self.penalty.keys():
            num_penalty[k] = 0
        num_penalty['dosen_ruang_waktu'] = self.check_dosen_ruang_waktu(chromosom)
        num_penalty['sks'] = self.check_sks(chromosom)
        for k in self.penalty:
            sum_penalty += (self.penalty[k] * num_penalty[k])
        chromosom_score = 1 / (1+sum_penalty)
        return chromosom_score

    def calculate_pop(self,population):
        population_score = []
        for pop in population:
            score = self.calculate_chromosom(pop)
            population_score.append(score)
        return population_score
