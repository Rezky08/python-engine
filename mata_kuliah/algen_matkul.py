
from mata_kuliah.rules_matkul import rules
import random
import numpy as np
import time
import threading
import queue
import copy
import sys
import math


class algen_matkul():
    def __init__(self, nn_params: dict, num_generation: int, num_population: int,
                 crossover_rate: float, mutation_rate: float, timeout=0, threading=True):
        """

        :param nn_params:{
                'mata_kuliah' : []
                'ruang_waktu' :[]
        }
        :param num_population:
        :param crossover_rate:
        :param mutation_rate:
        """
        self.nn_params = nn_params
        self.simply_nn_params = {}
        for key in nn_params.keys():
            self.simply_nn_params[key] = [index for index,
                                          item in enumerate(self.nn_params[key])]

        self.num_population = num_population
        self.num_generation = num_generation+1
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.rules = rules(self.nn_params)
        self.timeout = timeout
        self.threading = threading

    def generate_first_pop(self):
        chromosom_len = len(self.nn_params['mata_kuliah'])
        population = []
        for num_chromosom in range(self.num_population):
            chromosom = random.sample(
                self.simply_nn_params['ruang_waktu'], k=chromosom_len)
            population.append(chromosom)
        return population

    def selection(self, pop):
        # get fitness score
        fit_score = self.rules.calculate_pop(pop)
        fit_sum = sum(fit_score)

        # get fitness probability
        fit_prob = []
        for fit in fit_score:
            fit_prob.append(fit/fit_sum)

        # get fitness probabilty distribution
        fit_prob_dist = []
        for index, fit in enumerate(fit_prob, 1):
            fit_prob_dist.append(sum(fit_prob[:index]))

        # WHEEEELSSSS
        select = []
        for index, fit in enumerate(fit_prob_dist):
            rn = random.random()
            for indexin, fitin in enumerate(fit_prob_dist):
                if rn <= fitin:
                    select.append(indexin)
                    break
        chromosom_index_selected = []
        for index, chromosom in enumerate(select):
            rn = random.random()
            if rn <= self.crossover_rate:
                chromosom_index_selected.append(chromosom)
        parent = np.array(pop)[chromosom_index_selected]
        return parent

    def crossover(self, male, female):
        """
        using multi point crossover
        :return:
        """
        point = []
        child = []
        for _ in range(2):
            point.append(random.randint(0, len(male)-1))
        point = sorted(point)

        child.append(
            list(male[:point[0]])+list(female[point[0]:point[1]])+list(male[point[1]:]))
        child.append(
            list(female[:point[0]])+list(male[point[0]:point[1]])+list(female[point[1]:]))
        return child

    def pre_mutation(self, chromosom, que=None):
        start_time_mutation = time.time()
        duration = time.time() - start_time_mutation
        chromosom_score = self.rules.calculate_chromosom(chromosom)
        chromosom_score_before = self.rules.calculate_chromosom(chromosom)
        chromosom = self.mutation(chromosom)
        chromosom_score_after = self.rules.calculate_chromosom(chromosom)
        print("Pre Mutation Check : {} {} ".format(
            chromosom_score_after, chromosom_score_before))

        # chromosom_validate = copy.deepcopy(chromosom)
        # while duration < 30:
        #     chromosom_validate = self.mutation(chromosom_validate)
        #     chromosom_validate_score = self.rules.calculate_chromosom(chromosom_validate)
        #     duration = time.time() - start_time_mutation
        #     print("Pre Mutation Check : {} {} ".format(chromosom_validate_score,chromosom_score))
        #     if chromosom_validate_score > chromosom_score:
        #         chromosom = copy.deepcopy(chromosom_validate)
        #         break
        if que != None:
            que.put(chromosom)
        return chromosom

    def mutation(self, chromosom):
        for index, gene in enumerate(chromosom):
            if random.random() > random.random():
                chromosom_validate = copy.deepcopy(chromosom)
                chromosom_score = self.rules.calculate_chromosom(chromosom)
                try:
                    choosed_pass = []

                    while True:
                        choosed = random.choice(
                            self.simply_nn_params['ruang_waktu'])
                        while True:
                            if choosed in choosed_pass:
                                choosed = random.choice(
                                    self.simply_nn_params['ruang_waktu'])
                            else:
                                choosed_pass.append(choosed)
                                break

                        chromosom_validate[index] = choosed
                        chromosom_validate_score = self.rules.calculate_chromosom(
                            chromosom_validate)
                        if chromosom_validate_score > chromosom_score:
                            print("Mutation Check : {} {}".format(
                                chromosom_validate_score, chromosom_score))
                            chromosom = copy.deepcopy(chromosom_validate)
                            break

                        if len(choosed_pass) == len(self.simply_nn_params['ruang_waktu']):
                            break

                except:
                    pass
        print("masuk")
        return chromosom

    def evolve(self, pop):
        while True:
            parent = self.selection(pop)
            parent_len = len(parent)
            if parent_len > 1:
                break
        child_req = self.num_population - parent_len

        # LET'S BREED
        child = []
        while len(child) < child_req:
            while True:
                male = random.randint(0, parent_len - 1)
                female = random.randint(0, parent_len - 1)
                if male != female:
                    break
            babies = self.crossover(parent[male], parent[female])
            for _ in babies:
                if len(child) < child_req:
                    child.append(_)
        q = []
        th = []
        child_mutated = []
        for index, chromosom in enumerate(child):
            rn = random.random()
            if rn <= self.mutation_rate:
                print("Mutation Index : {}".format(index))
                if self.threading:
                    child_mutated.append(index)
                    q.append(queue.Queue())
                    th.append(threading.Thread(
                        target=self.pre_mutation, args=[chromosom, q[-1]]))
                    th[-1].start()
                else:
                    child[index] = self.pre_mutation(chromosom)
        if self.threading:
            for index, thread_index in enumerate(th):
                thread_index.join()
                child[child_mutated[index]] = q[index].get()

        parent = list(parent) + list(child)
        return parent

    def translate(self, chromosom):
        chromosom_simple = np.array(
            self.nn_params['ruang_waktu_simple'])[chromosom]
        chromosom = np.array(self.nn_params['ruang_waktu'])[chromosom]
        for index, item in enumerate(chromosom):
            sks = self.nn_params['mata_kuliah'][index]['sks_matkul']-1
            sesi_selesai = chromosom_simple[index]['sesi']+sks
            try:
                sesi = {
                    'sesi_mulai': item['sesi']['sesi_mulai'],
                    'sesi_selesai': self.nn_params['sesi'][sesi_selesai]['sesi_selesai']
                }
            except:
                sesi = item['sesi']
            chromosom[index]['sesi'] = sesi
        chromosom = list(chromosom)
        return chromosom

    def concat_with_key(self, chromsom):
        chromsom_cp = copy.deepcopy(chromsom)
        for index, item in enumerate(chromsom_cp):
            chromsom_cp[index] = {
                **self.nn_params['mata_kuliah'][index], **item}
        return chromsom_cp

    def run_generation(self):
        pop = self.generate_first_pop()
        pop_score = []
        max_score = []
        max_chromosom = []
        start_time = time.time()
        gen_avg = []
        for generation in range(1, self.num_generation):
            print("Generation {}".format(generation))
            pop_score = self.rules.calculate_pop(pop)
            avg = sum(pop_score) / len(pop_score)
            gen_avg.append(avg)
            gen_avg_unique = np.unique(gen_avg[-5:])

            print("Generation Average : ", avg)
            print("Score :", pop_score)

            if len(gen_avg) > 5:
                print("Generation Average Unique : {}".format(gen_avg_unique))
                if len(gen_avg_unique) == 1 or (
                        time.time() - start_time >= self.timeout and self.timeout != 0):
                    break
            if avg >= 1:
                break
            pop = self.evolve(pop)

        elapsed_time = time.time() - start_time
        chromosom_max_index = np.argwhere(
            np.array(pop_score) == max(pop_score))
        choosed_chromosom = random.choice(chromosom_max_index)
        # choosed_chromosom = map(lambda x: x[0], choosed_chromosom)
        # choosed_chromosom = list(choosed_chromosom)
        max_chromosom = np.array(pop)[choosed_chromosom].tolist()
        max_chromosom = self.translate(max_chromosom)
        max_chromosom = self.concat_with_key(max_chromosom)
        max_score = np.array(pop_score)[choosed_chromosom][0]

        return max_chromosom, max_score, elapsed_time
