import numpy as np
import pandas as pd
import math
class rules():
    def __init__(self,nn_params,rules_params):
        self.nn_params = nn_params
        self.rules_params=rules_params
        self.penalty = {
            'max_kelompok' : 1,
        }

    def check_kelompok(self,chromosom):
        """
        setiap dosen maksimal 3 kelompok
        :return:
        """

        max_kelompok = 0
        kode_dosen = map(lambda x:x['kode_dosen'],chromosom)
        kode_dosen = list(kode_dosen)
        kode_dosen, kode_dosen_count = np.unique(kode_dosen,return_counts=True)

        kode_matkul = map(lambda x: x['kode_matkul'], chromosom)
        kode_matkul = list(kode_matkul)
        kode_matkul, kode_matkul_count = np.unique(kode_matkul,return_counts=True)

        for index,kode_dosen in enumerate(kode_dosen):
            kode_matkul_by_dosen = filter(lambda x:x['kode_dosen'] == kode_dosen,chromosom)
            kode_matkul_by_dosen = list(kode_matkul_by_dosen)
            kode_matkul_by_dosen = map(lambda x:x['kode_matkul'],kode_matkul_by_dosen)
            kode_matkul_by_dosen = list(kode_matkul_by_dosen)
            kode_matkul_by_dosen,kode_matkul_by_dosen_count = np.unique(kode_matkul_by_dosen,return_counts=True)
            if len(kode_matkul_by_dosen)==1 and kode_dosen_count[index]>self.rules_params['max_kelompok']:

                special_cond = np.where(np.array(kode_matkul)==kode_matkul_by_dosen[0])
                special_cond = np.array(kode_matkul_count)[special_cond][0]

                dosen_in_matkul = np.where(np.array(self.nn_params['matkul_dosen']['kode_matkul'])==kode_matkul_by_dosen[0])
                dosen_in_matkul = np.array(self.nn_params['matkul_dosen']['kode_dosen'])[dosen_in_matkul][0]

                special_cond = special_cond/len(dosen_in_matkul)
                special_cond = math.ceil(special_cond)


                if kode_dosen_count[index]> special_cond:
                    max_kelompok += kode_dosen_count[index]
            elif kode_dosen_count[index]>self.rules_params['max_kelompok']:
                max_kelompok += kode_dosen_count[index]
        return max_kelompok
    def calculate_chromosom(self,chromosom):
        """
        formulas = 1 / (1+(penalty1 * num_penalty1)+...+(penaltyn * num_penaltyn))
        :return:
        """

        num_penalty = {}
        sum_penalty = 0

        for k in self.penalty.keys():
            num_penalty[k] = 0

        num_penalty['max_kelompok'] = self.check_kelompok(chromosom)

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
