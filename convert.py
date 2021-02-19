import os
import shutil
import pandas as pd

from tqdm import tqdm
def main(dir_oid,dir_out,move=True):
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    dir_csv=os.path.join(dir_oid,'csv_folder')

    path_cls=os.path.join(dir_csv,'class-descriptions-boxable.csv')
    with open(path_cls,'r') as fp:
        lines=fp.readlines()
    cls2ids={name:uid for uid,name in [line.strip().split(',') for line in lines]}

    path_names=os.path.join(dir_out,'oid.names')
    with open(path_names,'w') as fp:
        fp.writelines(list(cls2ids.keys()))

    dir_train=os.path.join(dir_oid,'Dataset','train')
    numClasses=[cls2ids[fn] for fn in os.listdir(dir_train) if os.path.isdir(os.path.join(dir_train,fn))]

    names_set=['train','test','validation']

    for name_set in names_set:
        f=pd.read_csv(os.path.join(dir_csv,'{}-annotations-bbox.csv'.format(name_set)))

    #For multiple classes use the below, adding as many new LabelNames as needed
    #this one is beer[0] cat[1] banana[2] in that order
    # numClasses = ['/m/07c52','/m/01knjb','/m/04bcr3','/m/078n6m','/m/0bh9flk','/m/02522','/m/01y9k5','/m/01c648']
        u = f.loc[f['LabelName'].isin(numClasses)]
        keep_col = ['LabelName','ImageID','XMin','XMax','YMin','YMax']

        new_f = u[keep_col]

        new_f['ClassNumber'] = new_f['LabelName']

    # adding a new column for Classnumber and setting the values based on LabelName
    # so, for this, it's beer[0] cat[1] banana[2] in that order
        for i,n in enumerate(numClasses):
            new_f.loc[new_f['LabelName'] == n, 'ClassNumber'] = i
    #new_f.loc[new_f['LabelName'] == '/m/01yrx', 'ClassNumber'] = 1
    #new_f.loc[new_f['LabelName'] == '/m/09qck', 'ClassNumber'] = 2


        new_f['width'] = new_f['XMax'] - new_f['XMin']
        new_f['height'] = new_f['YMax'] - new_f['YMin']
        new_f['x'] = (new_f['XMax'] + new_f['XMin'])/2
        new_f['y'] = (new_f['YMax'] + new_f['YMin'])/2
        keep_col = ['ClassNumber','ImageID','x','y','width','height']
        new_f_2 = new_f[keep_col]

        dir_imgs=os.path.join(dir_oid,'Dataset',name_set)
        dir_out_set=os.path.join(dir_out,name_set)
        if not os.path.exists(dir_out_set):
            #print(dir_out_set)
            os.mkdir(dir_out_set)
        lines_txt=[]
        for dirname in os.listdir(dir_imgs):
            path_dir=os.path.join(dir_imgs,dirname)
            for filename in tqdm(os.listdir(path_dir),desc="Processing files of {} set, class:{}".format(name_set,dirname)):
                if filename.endswith(".jpg"):
                    fn = filename[:-4]
                    nf = new_f_2.loc[new_f_2['ImageID'] == fn]
                    keep_col = ['ClassNumber','x','y','width','height']
                    new_nf = nf[keep_col]
                    #print(new_nf)
                    txtpath =os.path.join(dir_out_set,fn + ".txt")

                    #print(imgpath)
                    new_nf.to_csv(txtpath, index=False, header=False, sep=' ')
                    if not txtpath in lines_txt:
                        lines_txt.append(txtpath)

                    srcpath=os.path.join(path_dir,filename)
                    imgpath=os.path.join(dir_out_set,filename)
                    if move:
                        pass
                        #shutil.move(srcpath,imgpath)
                    else:
                        shutil.copy2(srcpath,imgpath)
        path_set_txt=os.path.join(dir_out,name_set+'.txt')
        with open(path_set_txt,'w') as fp:
            fp.writelines(lines_txt)

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_oid', type=str, help='Root dir of OID')
    parser.add_argument('dir_out', type=str, help='Output dir')
    parser.add_argument('--move', action='store_true',default=False, help='Move .jpg files or not (copy)')

    args=parser.parse_args()
    print(bool(args.move))
    main(args.dir_oid,args.dir_out,move=args.move)