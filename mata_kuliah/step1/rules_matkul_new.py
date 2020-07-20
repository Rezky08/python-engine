import numpy as np
import math
import copy
import datetime


class rules():
    def __init__(self,nn_params):
        self.nn_params = nn_params
        self.penalty = {
            'hari_mata_kuliah' : 1,
            'hari_sks' : 1,
            'hari_dosen':1
        }

    def check_hari_dosen(self, chromosom):
        hari_dosen_score = 0
        kode_dosen = map(lambda x:x['kode_dosen'],self.nn_params['mata_kuliah'])
        kode_dosen = list(kode_dosen)
        kode_dosen_unique,kode_dosen_count = np.unique(kode_dosen,return_counts=True)

        chromosom_cp = copy.deepcopy(chromosom)
        chromosom_cp = [[self.nn_params['mata_kuliah'][index]['kode_dosen'],item] for index,item in enumerate(chromosom_cp)]
        chromosom_cp_unique,chromosom_cp_count = np.unique(chromosom_cp,return_counts=True,axis=0)

        max_dosen = {item:[] for item in kode_dosen_unique}
        for item in kode_dosen_unique:
            sks = filter(lambda x:x['kode_dosen']==item,self.nn_params['mata_kuliah'])
            sks = map(lambda x:x['sks_matkul'],sks)
            sks = list(sks)
            max_sks = max(sks)
            max_dosen[item] = math.floor(len(self.nn_params['sesi'])/max_sks)

        for index,item in enumerate(chromosom_cp_unique):
            if chromosom_cp_count[index]>max_dosen[item[0]]:
                hari_dosen_score+=chromosom_cp_count[index]
        return hari_dosen_score
    def check_hari_sks(self, chromosom):
        hari_sks_score = 0
        sks_hari = {index:[] for index,item in enumerate(self.nn_params['hari'])}
        max_ruang = {}
        max_sks_hari = copy.deepcopy(sks_hari)
        for index, item in enumerate(chromosom):
            sks_hari[item[1]].append(self.nn_params['mata_kuliah'][index]['sks_matkul'])

        low_limit = datetime.time(11)
        up_limit = datetime.time(13)
        black_list = []
        for index, item in enumerate(self.nn_params['sesi']):
            if (item['sesi_mulai'] > low_limit and item['sesi_mulai'] < up_limit) or (
                    item['sesi_selesai'] > low_limit and item['sesi_selesai'] < up_limit):
                black_list.append(index)
        for index,item in enumerate(self.nn_params['hari']):
            hari = ''.join(filter(str.isalpha,item))
            if hari == 'jumat':
                max_sks = len(self.nn_params['ruang']) * (len(self.nn_params['sesi'])-len(black_list))
            else:
                max_sks = len(self.nn_params['ruang']) * len(self.nn_params['sesi'])
            max_sks_hari[index] = max_sks

        for item in sks_hari:
            total = sum(sks_hari[item])
            if total>max_sks_hari[item]:
                hari_sks_score+=1
        return hari_sks_score

    def check_hari_mata_kuliah(self,chromosom):
        hari_mata_kuliah_score = 0
        chromosom_unique, chromosom_count = np.unique(chromosom,return_counts=True,axis=0)
        for index, item in enumerate(chromosom_unique):
            max_count = self.nn_params['max_hari_mata_kuliah'][item[0]]
            if chromosom_count[index]>max_count:
                hari_mata_kuliah_score+=chromosom_count[index]
        return hari_mata_kuliah_score
    def calculate_chromosom(self,chromosom):
        """
        formulas = 1 / (1+(penalty1 * num_penalty1)+...+(penaltyn * num_penaltyn))
        :return:
        """

        num_penalty = {}
        sum_penalty = 0
        chromosom_cp = []
        for index,item in enumerate(self.nn_params['mata_kuliah']):
            gen = {
                'kode_matkul' : item['kode_matkul'],
                'hari' : chromosom[index]
            }
            chromosom_cp.append(gen)
        chromosom_simply = map(lambda x:list(x.values()),chromosom_cp)
        chromosom_simply = list(chromosom_simply)


        for k in self.penalty.keys():
            num_penalty[k] = 0
        num_penalty['hari_mata_kuliah'] = self.check_hari_mata_kuliah(chromosom_simply)
        num_penalty['hari_sks'] = self.check_hari_sks(chromosom_simply)
        num_penalty['hari_dosen'] = self.check_hari_dosen(chromosom)

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
