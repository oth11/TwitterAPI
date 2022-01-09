# Load the package required to read JSON files.
# Works in conjunction with Twitter Loop Python script

library(jsonlite)
library(tidyr)

root_path <- "ROOTPATH"    #set your root path
setwd(root_path)                                #change working directory

myFolder <- "TWEETSFOLDER"                      # set your tweets folder

writeCSV <- function() {
  myPath <- paste(root_path, myFolder, sep = "/")
  setwd(myPath)
  myList <- list.files(myPath, pattern = ".json", )
  print(myList)

  lapply(myList, function(x) {
    print(paste("reading file: ", x, sep = ""))
    result <- read_json(x,simplifyVector = TRUE, flatten = TRUE)
    library(splitstackshape)
    listCol_l(result, 'referenced_tweets')
    result <- unnest(result, referenced_tweets, keep_empty = TRUE, names_sep = "_")
    flatten(result, recursive = TRUE)
    head(result,10)
    outputfile <- paste(gsub('.json','', x), ".csv", sep = "")
    function(result, outputfile)
      print(paste("writing file: ", outputfile, sep = ""))
    write.csv(result, file=outputfile, row.names = FALSE)
  })
}

setwd(root_path)

