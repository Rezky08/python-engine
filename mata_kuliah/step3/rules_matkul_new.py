import numpy as np
import copy
import datetime

class rules():
    def __init__(self,nn_params):
        self.nn_params = nn_params
        self.penalty = {
            'jadwal_bentrok' : 1,
            'jadwal_dosen_duplicate' : 1,
            'jadwal_over' : 1,
            'jadwal_jumat':1
        }
    def check_jadwal_dosen_duplicate(self,chromosom):
        jadwal_dose_duplicate_score = 0
        mata_kuliah = copy.deepcopy(self.nn_params['mata_kuliah'])
        chromosom_cp = [[mata_kuliah[index]['kode_dosen'],mata_kuliah[index]['hari'],item] for index,item in enumerate(chromosom)]
        chromosom_cp_unique,chromosom_cp_count = np.unique(chromosom_cp,return_counts=True,axis=0)
        chromosom_fails = filter(lambda x:x>1,chromosom_cp_count)
        chromosom_fails = list(chromosom_fails)
        jadwal_dose_duplicate_score+=len(chromosom_fails)
        return jadwal_dose_duplicate_score
    def check_jadwal_bentrok(self,chromosom):
        jadwal_bentrok_score = 0
        chromosom_cp = [[item['hari'],item['ruang'],chromosom[index]] for index,item in enumerate(self.nn_params['mata_kuliah'])]
        # check duplicate
        chromosom_cp_unique, chromosom_cp_count = np.unique(chromosom_cp,return_counts=True,axis=0)
        chromosom_fails_index = np.where(chromosom_cp_count>1)
        chromosom_fails = chromosom_cp_unique[chromosom_fails_index].tolist()
        chromosom_fails_count = chromosom_cp_count[np.where(chromosom_cp_count>1)].tolist()
        chromosom_fails_count = sum(chromosom_fails_count)

        for index,item in enumerate(self.nn_params['mata_kuliah']):
            if chromosom_cp[index] in chromosom_fails:
                continue
                added_list = []
                for sks in range(1,item['sks_matkul']):
                    added = copy.deepcopy(chromosom_cp[index])
                    added[2]+=sks
                    added_list.append(added)
                for item in added_list:
                    if item in chromosom_cp:
                        jadwal_bentrok_score+=1
                        break
        jadwal_bentrok_score+=chromosom_fails_count
        return jadwal_bentrok_score

    def check_jadwal_over(self,chromosom):
        jadwal_over_score =0
        max_sesi = len(self.nn_params['sesi'])-1
        for index,item in enumerate(chromosom):
            end_sesi = item+self.nn_params['mata_kuliah'][index]['sks_matkul']-1
            if end_sesi>max_sesi:
                jadwal_over_score+=1
        return  jadwal_over_score
    def check_jadwal_jumat(self,chromosom):
        jadwal_jumat_score = 0
        hari = self.nn_params['hari']
        hari = map(lambda x:''.join(filter(str.isalpha,x)),hari)
        hari = list(hari)
        jumat_index = np.where(np.array(hari)=="jumat")[0]
        if not jumat_index:
            return jadwal_jumat_score

        jumat_index = jumat_index[0]
        chromosom_cp = [[self.nn_params['mata_kuliah'][index]['hari'],item] for index,item in enumerate(chromosom)]
        low_limit = datetime.time(11)
        up_limit = datetime.time(13)
        black_list = []
        for index,item in enumerate(self.nn_params['sesi']):
            if (item['sesi_mulai']>low_limit and item['sesi_mulai']<up_limit) or (item['sesi_selesai']>low_limit and item['sesi_selesai']<up_limit):
                black_list.append(index)
        if not black_list:
            return jadwal_jumat_score

        black_list = [[jumat_index,item] for item in black_list]
        for index,item in enumerate(chromosom_cp):
            added = [[item[0],item[1]+sks] for sks in range(self.nn_params['mata_kuliah'][index]['sks_matkul'])]
            for item_added in added:
                if item_added in black_list:
                    jadwal_jumat_score += 1
                    break
        return jadwal_jumat_score

    def calculate_chromosom(self,chromosom):
        """
        formulas = 1 / (1+(penalty1 * num_penalty1)+...+(penaltyn * num_penaltyn))
        :return:
        """
        num_penalty = {}
        sum_penalty = 0

        for k in self.penalty.keys():
            num_penalty[k] = 0
        num_penalty['jadwal_bentrok'] = self.check_jadwal_bentrok(chromosom)
        num_penalty['jadwal_dosen_duplicate'] = self.check_jadwal_dosen_duplicate(chromosom)
        num_penalty['jadwal_over'] = self.check_jadwal_over(chromosom)
        num_penalty['jadwal_jumat'] = self.check_jadwal_jumat(chromosom)
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
