# Load the package required to read JSON files.
library(jsonlite)
library(tidyr)

# root_path <- "/home/rstudio/Dropbox/RStudio"
# setwd(root_path)

meta_folder <- "meta_polit"
tweets_folder <- "tweets_polit"
myPath <- paste(root_path, tweets_folder, sep = "/")
myMetaPath <- paste(root_path, meta_folder, sep = "/")

# setwd(myPath)
# myList <- list.files(myPath, pattern = ".json", )
# print(myList)

writeCSV <- function(myDir) {
    root_path <- "/home/rstudio/Dropbox/RStudio"
    setwd(myDir)
    myList <- list.files(myDir, pattern = ".json", )
    
    lapply(myList, function(x) {
    print(paste("reading file: ", x, sep = ""))
    # result <- stream_in(file(x))
    result <- read_json(x,simplifyVector = TRUE, flatten = TRUE)
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
