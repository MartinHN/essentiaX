from utils.algorithms_info import *
import os



if __name__ == '__main__':
    essentiasrc = sys.argv[1]
    algodir = os.path.join(essentiasrc,"algorithms")
    
    # create_version_h();
    algos = get_all_algorithms(algodir,essentiasrc)
    ignore = ['GaiaTransform','FFTK', 'IFFTK', 'FFTW', 'IFFTW']
    for i in ignore:
        del algos[i]
    

    regFile = os.path.join(algodir,"essentia_algorithms_reg.cpp")
    create_registration_cpp(algos,regFile)

    # for name, algo in algos.items():
    #     print name, ':\n',
    #     for attr in algo:
    #         print '  %s: %s' % (attr, algo[attr])
    #     print