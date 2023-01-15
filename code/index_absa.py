import pickle
from glob import glob

if __name__ == '__main__':
    filenames = []
    total_number = 0
    for file in glob('data/swe-absa-bank/ABSA+annotation_2019-01-23_0534/annotation/*'):
        total_number += 1
        if 'flashback' in file:
            filenames.append(file.split('/')[-1])

    print(total_number)
    print(filenames[:10])
    print(len(filenames))
    with open('data/saved/index_absa.txt', 'w', encoding='utf-8') as f:
        for filename in filenames:
            f.write(filename + '\n')
