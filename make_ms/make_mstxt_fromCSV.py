
import os
import pandas as pd
import argparse




def make_txt(df, out):
    ms = "ms1610"
    mse_list = []
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        mse = df.loc[idx, "mse"]
        if msid == ms:
            out_file = out + ms +'.txt'
            with open(out_file, "a") as text_file:
                #print(msid, mse)
                text_file.write(mse + "\n")

            #mse_list.append(mse)
        else:
            ms = msid
            mse_list = []



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code creates an text file of mses given an msid')
    parser.add_argument('-i', help = 'csv containing the msid')
    parser.add_argument('-o', help = 'output directory')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    df = pd.read_csv("{}".format(c))
    make_txt(df, out)




