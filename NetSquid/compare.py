from MDI import MDIKeyExchange
from BB84_loss_model import BB84KeyExchange
import csv
from fractions import Fraction

NANOSECOND = 1
MILSECOND = 1e3
SECOND = 1e9
# bb84 = BB84KeyExchange(6, 1000, MILSECOND)
# mdi = MDIKeyExchange(1, 5, 1000, MILSECOND)

# print(f'{bb84.run()*1e6} bits/s')
# print(f'{mdi.run()*1e6} bits/s')

# with open('MDI_BB84_benchmark.csv', 'w', newline='') as csvfile:
#     fieldnames = ['dist', 'bb84_key_rate_kbps', 'mdi_key_rate_kbps']
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#     writer.writeheader()
#     for total_dist in [10, 25, 50, 100, 200]:
#         ac_dist = total_dist / 2
#         bc_dist = total_dist / 2
#         mdi = MDIKeyExchange(ac_dist, bc_dist, 100*total_dist, MILSECOND)
#         bb84 = BB84KeyExchange(total_dist, 100*total_dist, MILSECOND)
#         writer.writerow({
#             'dist': round(total_dist, 2),
#             'bb84_key_rate_kbps': bb84.run()*(SECOND/MILSECOND)/1000,
#             'mdi_key_rate_kbps': mdi.run()*(SECOND/MILSECOND)/1000
#         })
#         print(f'total dist: {total_dist}')
#         print(f'MDI key rate: {mdi.run()*(SECOND/MILSECOND)} bits/s, ac: {ac_dist}, bc: {bc_dist}')
#         print(f'BB84 key rate: {bb84.run()*(SECOND/MILSECOND)}')

with open('MDI_asymmetry_benchmark.csv', 'w', newline='') as csvfile:
    fieldnames = ['ac_dist', 'bc_dist', 'ratio', 'key_rate_kbps']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    total_dist = 20
    for division in [2, 4, 8, 16, 32]:
        ac_dist = total_dist / division
        bc_dist = total_dist - ac_dist
        mdi = MDIKeyExchange(ac_dist, bc_dist, 100*total_dist, MILSECOND)
        writer.writerow({
            'ac_dist': round(ac_dist, 2), 
            'bc_dist': round(bc_dist, 2),
            'ratio': f'{1}:{division - 1}',
            'key_rate_kbps': mdi.run()*(SECOND/MILSECOND)/1000
        })
        print(f'Difference: {round(bc_dist/ac_dist, 0)}, MDI key rate: {mdi.run()*(SECOND/MILSECOND)} bits/s')
