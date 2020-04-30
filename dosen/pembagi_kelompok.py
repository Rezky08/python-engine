import math
import numpy as np

class pembagi_kelompok():
    def __init__(self,peminat_params:dict,peminat_prop:dict):
        self.peminat = peminat_params
        self.prop = peminat_prop

    def seleksi_matkul(self):
        self.peminat_kelas = filter(lambda x:x['jumlah_peminat'] >= self.prop['min_perkelas'] and x['lab_matkul'] == False,self.peminat)
        self.peminat_kelas = list(self.peminat_kelas)
        self.peminat_lab = filter(lambda x:x['jumlah_peminat'] >= self.prop['min_perlab'] and x['lab_matkul'] == True,self.peminat)
        self.peminat_lab = list(self.peminat_lab)
        self.peminat = self.peminat_lab+self.peminat_kelas


    def pembagian_kapasitas(self,peminat: dict,max_perkelompok:int):
        pembagian_kelompok = []
        for index, matkul in enumerate(peminat):
            matkul_kelompok = {
                'kode_matkul': matkul['kode_matkul'],
            }
            dividen = max_perkelompok
            while True:
                ceiling = math.ceil(matkul['jumlah_peminat'] / dividen)
                if ceiling * dividen >= matkul['jumlah_peminat']:
                    kapasitas_kelompok = math.ceil(matkul['jumlah_peminat'] / ceiling)
                    pembagian = matkul['jumlah_peminat'] % kapasitas_kelompok
                    if pembagian != 0:
                        matkul_kelompok['jumlah_kelompok'] = [ceiling - 1, 1]
                        matkul_kelompok['kapasitas_kelompok'] = [kapasitas_kelompok, pembagian]
                    else:
                        matkul_kelompok['jumlah_kelompok'] = [ceiling]
                        matkul_kelompok['kapasitas_kelompok'] = [kapasitas_kelompok]
                    break
                dividen -= 1
            pembagian_kelompok.append(matkul_kelompok)
        return pembagian_kelompok


    def pembagian_nama_kelompok(self,kelompok_kapasitas: dict):
        mata_kuliah_kelompok = []
        for index, matkul in enumerate(kelompok_kapasitas):
            nama_kelompok = ["A", "A"]
            for idj, jumlah_kelompok in enumerate(matkul['jumlah_kelompok']):
                for i in range(jumlah_kelompok):
                    matkul_kelompok = {
                        'kode_matkul': matkul['kode_matkul'],
                        'kelompok': "".join(nama_kelompok),
                        'kapasitas': matkul['kapasitas_kelompok'][idj]
                    }
                    kode_kelas = ord(nama_kelompok[1])
                    kode_kelas += 1
                    nama_kelompok[1] = chr(kode_kelas)
                    mata_kuliah_kelompok.append(matkul_kelompok)
        return mata_kuliah_kelompok

    def bagi_kelompok(self):
        self.seleksi_matkul()
        kapasitas_peminat_kelas = self.pembagian_kapasitas(self.peminat_kelas,self.prop['max_perkelas'])
        kapasitas_peminat_lab = self.pembagian_kapasitas(self.peminat_lab, self.prop['max_perlab'])
        kapasitas_peminat = kapasitas_peminat_kelas+kapasitas_peminat_lab
        kelompok_matkul = self.pembagian_nama_kelompok(kapasitas_peminat)
        return kelompok_matkul


