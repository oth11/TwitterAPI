# Load the package required to read JSON files.
library(jsonlite)
library(tidyr)

root_path <- "/home/rstudio/Dropbox/RStudio"    #set your root path
setwd(root_path)                                #change working directory

# fb_folder <- "_WISE2021/2021-10-fb-polit/_archiviert"
# meta_folder <- "_WISE2021/2021-10-meta-ceo"
# tweets_folder <- "_WISE2021/2021-10-tweets-ceo"
# meta_folder <- "_WISE2021/2021-10-meta-polit"
# tweets_folder <- "_WISE2021/2021-10-tweets-polit"
# myPath <- paste(root_path, fb_folder, sep = "/")
# myPath <- paste(root_path, tweets_folder, sep = "/")
# myMetaPath <- paste(root_path, meta_folder, sep = "/")

setwd(myPath)
# myList <- list.files(myPath, pattern = ".txt", )
myList <- list.files(myPath, pattern = ".json", )
print(myList)

writeCSV <- function(tweets_folder) {
    root_path <- "/home/rstudio/Dropbox/RStudio"
    myPath <- paste(root_path, tweets_folder, sep = "/")
    setwd(myPath)
    myList <- list.files(myPath, pattern = ".json", )
    # myList <- list.files(myPath, pattern = ".txt", )
    print(myList)
    
    lapply(myList, function(x) {
      print(paste("reading file: ", x, sep = ""))
      # result <- stream_in(file(x))
      result <- read_json(x,simplifyVector = TRUE, flatten = TRUE)
      library(splitstackshape)
      listCol_l(result, 'referenced_tweets')
      result <- unnest(result, referenced_tweets, keep_empty = TRUE, names_sep = ".")
      flatten(result, recursive = TRUE)
      head(result,10)
      # outputfile <- paste(gsub('.txt','', x), ".csv", sep = "")
      outputfile <- paste(gsub('.json','', x), ".csv", sep = "")
      function(result, outputfile)
      print(paste("writing file: ", outputfile, sep = ""))
      write.csv(result, file=outputfile, row.names = FALSE)
      # write to file
      # write.table(out, "path/to/output", sep="\t", quote=FALSE, row.names=FALSE, col.names=TRUE)
    })
}

# Give the input file name to the function.
# result <- read_json(inputfile,simplifyVector = TRUE, flatten = TRUE)
# write.csv(result, file=outputfile, row.names = FALSE)

setwd(root_path)

