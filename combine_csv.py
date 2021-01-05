import os
import glob
import pandas as pd

meta_folder = "meta_polit/"
tweets_folder = "tweets_polit/"
extension = 'csv'


def myfiles(userfolder,extension):
  all_filenames = [i for i in glob.glob('{}*.{}'.format(userfolder,extension))]
  #combine all files in the list
  combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
  #export to csv
  combined_name = ('{}combined_csv.csv').format(userfolder)
  combined_csv.to_csv(combined_name, index=False, encoding='utf-8-sig')


def main():
  myfiles(tweets_folder,extension)
  myfiles(meta_folder,extension)

if __name__ == "__main__":
    main()


