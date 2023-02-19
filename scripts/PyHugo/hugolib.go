package main

import (
  "C"
  "log"

//	"fmt"
//	"os"
  "path/filepath"
//	"strings"

  "encoding/json"
  "github.com/gohugoio/hugo/config"
  "github.com/gohugoio/hugo/hugofs"
  "github.com/gohugoio/hugo/hugolib"
  "github.com/gohugoio/hugo/common/loggers"

  "github.com/spf13/afero"
)

/*
type  MapEntry {
    Key string  `json:"key"`
    Value string `json:"value"`
}
*/

var (
  env = "production"
  ConfigDefaults = []string{"baseURL", "resourceDir", "contentDir", "dataDir", "i18nDir", "layoutDir", "assetDir", "archetypeDir", "publishDir", "workingDir", "defaultContentLanguage"}

)


//export loadConfig
func loadConfig (filePtr *C.char) (*C.char) {
  filename := C.GoString(filePtr)
  if !filepath.IsAbs(filename) {
    filename, _ = filepath.Abs(filename)
  }
  wd := filepath.Dir(filename)

  if !config.IsValidConfigFilename(filename) {
    log.Printf("Error: %s is not a valid filename", filename)
    return C.CString("{}")
  }


  log.Printf("loading %s from %s", filename, wd)
  var configFiles []string
  var sourceFs afero.Fs = hugofs.Os

  //var Cfg config.Provider
  cfg, configFiles, err := hugolib.LoadConfig(hugolib.ConfigSourceDescriptor{Fs: sourceFs, Filename: filename, WorkingDir: wd, Environment: env, Path: wd, Logger: loggers.NewWarningLogger()})

  if err != nil {
		log.Printf("Error: %s", err.Error())
	}

  if cfg == nil {
    return C.CString("{}")
  } else {
    log.Printf("config %s", cfg)
  }

  baseConfig := make(map[string]any)
  for _, k := range ConfigDefaults {
    baseConfig[k] = cfg.GetString(k)
  }

  for _, l := range Keys(config.ConfigRootKeysSet) {
    baseConfig[l] = cfg.GetStringMap(l)
  }

/*
  for _, k := range append(ConfigDefaults, rootKeys...) {
    log.Printf("%s -> %s \n", k, cfg.GetStringMap(k))
  }
*/

  for m := range configFiles {
    log.Printf("%s \n", m)
  }

  jsonStr, err := json.Marshal(&baseConfig)
  if err != nil {
      log.Printf("Error: %s", err.Error())
      return C.CString("{}")
  } else {
      log.Println(string(jsonStr))
      return C.CString(string(jsonStr))
  }

}

//export buildStructure
func buildStructure (filePtr, wdPointer *C.char) (*C.char) {
  return C.CString("{}")
}

func Keys[T any](m map[string]T) (keys []string) {
    for k := range m {
        keys = append(keys, k)
    }
    return keys
}


//export fromJSON
func fromJSON(documentPtr *C.char){
   documentString := C.GoString(documentPtr)
   var jsonDocument map[string]interface{}
   err := json.Unmarshal([]byte(documentString), &jsonDocument)
   if err != nil{
      log.Fatal(err)
   }
   log.Println(jsonDocument)
}

func main(){

}
