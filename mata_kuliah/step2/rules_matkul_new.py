import numpy as np

class rules():
    def __init__(self,nn_params):
        self.nn_params = nn_params
        self.penalty = {
            'max_ruang' : 1,
            'max_sks' : 1
        }
    def check_max_ruang(self,chromosom):
        max_ruang_score = 0
        chromosom_unique, chromosom_count = np.unique(chromosom,return_counts=True,axis=0)
        for index, item in enumerate(chromosom_unique):
            max_count = self.nn_params['max_ruang'][item[0]]
            if chromosom_count[index]>max_count:
                max_ruang_score+=chromosom_count[index]
        return max_ruang_score
    def check_max_sks(self,chromosom):
        max_sks_score = 0
        hari = map(lambda x:x['hari'],self.nn_params['mata_kuliah'])
        hari = list(hari)
        hari_ruang = [[item,chromosom[index]] for index,item in enumerate(hari)]
        hari_ruang_unique=np.unique(hari_ruang,axis=0).tolist()
        for item in hari_ruang_unique:
            hari_ruang_index = [index for index,item_hari_ruang in enumerate(hari_ruang) if item_hari_ruang==item]
            mata_kuliah_sks = np.array(self.nn_params['mata_kuliah'])[hari_ruang_index]
            mata_kuliah_sks = map(lambda x:x['sks_matkul'],mata_kuliah_sks)
            mata_kuliah_sks = list(mata_kuliah_sks)
            mata_kuliah_sks = sum(mata_kuliah_sks)
            if mata_kuliah_sks > len(self.nn_params['sesi']):
                max_sks_score+=1
        return max_sks_score

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
                'hari' : item['hari'],
                'ruang' : chromosom[index]
            }
            chromosom_cp.append(gen)
        chromosom_simply = map(lambda x:list(x.values()),chromosom_cp)
        chromosom_simply = list(chromosom_simply)

        for k in self.penalty.keys():
            num_penalty[k] = 0
        num_penalty['max_ruang'] = self.check_max_ruang(chromosom_simply)
        num_penalty['max_sks'] = self.check_max_sks(chromosom)
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
