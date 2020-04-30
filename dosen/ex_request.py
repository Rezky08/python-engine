import pandas as pd
import numpy as np
from pembagi_kelompok import pembagi_kelompok
from algen_only_dosen import algen_only_dosen
import time



mata_kuliah = pd.read_csv('D:/KULIAH/KKP/bahan/sudah diolah/jadwal_semester_genap_mata_kuliah.csv')
dosen_by_matkul = pd.read_csv('D:/KULIAH/KKP/bahan/sudah diolah/jadwal_semester_genap_dosen_by_matkul.csv')
peminat_genap = pd.read_csv('D:/KULIAH/KKP/bahan/sudah diolah/peminat_genap.csv').to_dict(orient='record')

# bagi kelompok preparation
for index, peminat in enumerate(peminat_genap):
    try:
        peminat['lab'] = mata_kuliah.loc[mata_kuliah['kode_matkul'] == peminat['kode_matkul']].lab.values[0]
    except:
        peminat['lab'] = False
peminat_prop ={
    'min_perkelas' : 20,
    'max_perkelas' : 50,
    'min_perlab' : 15,
    'max_perlab' : 50,
}
peminat = pembagi_kelompok(peminat_genap,peminat_prop)
peminat = peminat.bagi_kelompok()

# matkul accepted
kode_matkul = map(lambda x:x['kode_matkul'],peminat)
kode_matkul = list(kode_matkul)
kode_matkul = np.unique(np.array(kode_matkul))

mata_kuliah = mata_kuliah.to_dict(orient='record')
mata_kuliah = filter(lambda x:x['kode_matkul'] in kode_matkul,mata_kuliah)
mata_kuliah = list(mata_kuliah)
kode_matkul = map(lambda x:x['kode_matkul'],mata_kuliah)
kode_matkul = list(kode_matkul)
peminat = filter(lambda x:x['kode_matkul'] in kode_matkul,peminat)
peminat = list(peminat)


# grouping dosen by matkul
dosen_by_matkul_group = dosen_by_matkul.groupby(by=['kode_matkul'])
dosen_by_matkul = []
for kode,dosen in dosen_by_matkul_group:
    frame ={
        'kode_matkul':kode,
        'kode_dosen':dosen.to_dict(orient='list')['kode_dosen']
    }
    dosen_by_matkul.append(frame)
dosen_by_matkul = pd.DataFrame(dosen_by_matkul).to_dict(orient='list')

# algen dosen prep

# nn_params untuk pembagian dosen
nn_params = {
    'mata_kuliah' : peminat,
    'matkul_dosen' : dosen_by_matkul
}
rules ={
    'max_kelompok' : 3
}

num_generation = 100
num_population = 50
mutation_rate = 0.7
crossover_rate = 0.75


algen = algen_only_dosen(nn_params,rules,num_generation,num_population,crossover_rate,mutation_rate)

# start search algen
start_time = time.time()
result = algen.run_generation()
pd.DataFrame.from_records(result[0]).to_csv('susunan_dosen.csv')
print("running time : {}".format(time.time()-start_time))


