package main

import (
  "C"
//	"fmt"
  "log"
	"os"
  "path/filepath"
  "io/ioutil"
//	"strings"
  "bytes"
  "errors"

  "encoding/json"
  "github.com/gohugoio/hugo/config"
  "github.com/gohugoio/hugo/hugofs"
  "github.com/gohugoio/hugo/hugolib"
  "github.com/gohugoio/hugo/common/loggers"
  "github.com/gohugoio/hugo/deps"
  "github.com/gohugoio/hugo/langs"

  "github.com/spf13/afero"
)

/*
type  MapEntry {
    Key string  `json:"key"`
    Value string `json:"value"`
}
*/

var (
  Debug = false
  Env = "production"
  ConfigDefaults = []string{"baseURL", "resourceDir", "contentDir", "dataDir", "i18nDir", "layoutDir", "assetDir", "archetypeDir", "publishDir", "workingDir", "defaultContentLanguage"}

  buf bytes.Buffer
	logger = log.New(&buf, "", log.Lshortfile | log.Ltime)
  fs afero.Fs = hugofs.Os
)

func init() {
    logger.SetOutput(ioutil.Discard)
}
/*
func (log *log.Logger) Write(data []byte) (n int, err error) {
    log.Print(data)
    return len(data), nil
}
*/

//export LoadConfigFromFile
func LoadConfigFromFile (filenamePtr *C.char) (*C.char) {
  filename := C.GoString(filenamePtr)
  if !config.IsValidConfigFilename(filename) {
    logger.Printf("Error: %s is not a valid filename", filename)
    return C.CString("{}")
  }

  if !filepath.IsAbs(filename) {
    filename, _ = filepath.Abs(filename)
  }
  siteDir := filepath.Dir(filename)

  logger.Printf("loading %s from %s", filename, siteDir)

  cfg := loadConfig(siteDir, filename)

  return C.CString(cfgToStr(cfg))
}

//export LoadConfig
func LoadConfig (siteDirPtr *C.char) (*C.char) {
  siteDir := C.GoString(siteDirPtr)

  s, _ := afero.IsDir(fs, siteDir)
  if !s {
    siteDir = filepath.Dir(siteDir)
  }
  filename, err := findConfig(siteDir)
  if err != nil {
    logger.Printf("Error: %s is not a valid filename", err)
  }

  logger.Printf("loading %s from %s", filename, siteDir)

  //var Cfg config.Provider
  cfg, _, err := hugolib.LoadConfig(hugolib.ConfigSourceDescriptor{Fs: fs, Filename: filename, WorkingDir: siteDir, Environment: Env, Path: siteDir, Logger: loggers.NewWarningLogger()})

  if err != nil {
		logger.Printf("Error: %s", err.Error())
	}

  if cfg == nil {
    return C.CString("{}")
  } else {
    logger.Printf("Config is %s", cfg)
  }

  baseConfig := make(map[string]any)
  for _, k := range ConfigDefaults {
    baseConfig[k] = cfg.GetString(k)
  }


  //allmodules
  for _, l := range Keys(config.ConfigRootKeysSet) {
    baseConfig[l] = cfg.GetStringMap(l)
  }

  jsonStr, err := json.Marshal(&baseConfig)
  if err != nil {
      logger.Printf("Error: %s", err.Error())
      return C.CString("{}")
  } else {
      logger.Println(string(jsonStr))
      return C.CString(string(jsonStr))
  }
}

func resolveConfig (filePtr *C.char) (string, string, error) {
  file := C.GoString(filePtr)
  s, _ := afero.IsDir(fs, file)
  if !s {
    file = filepath.Dir(file)
  }
  filename, err := findConfig(file)
  return file, filename, err
}

//export BuildStructure
func BuildStructure (siteDirPtr *C.char) (*C.char) {
  siteDir, filename, _ := resolveConfig(siteDirPtr)
  cfg := loadConfig(siteDir, filename)
  l := langs.NewDefaultLanguage(cfg)
  cfg.Set("languagesSorted", langs.NewLanguages(l))

  opts := hugolib.BuildCfg{NewConfig: cfg, SkipRender: true, ResetState: true}
  depsCfg := deps.DepsCfg{Fs: hugofs.NewDefault(cfg), Cfg: cfg}
  sites, err := hugolib.NewHugoSites(depsCfg)

  if err != nil {
		logger.Printf("Error building site: %s", err.Error())
	}

  sites.Build(opts)
  if Debug {
    logger.Printf("Main lang is %s", l)
    sites.PrintProcessingStats(log.Writer())
  }

  if sites == nil {
    return C.CString("{}")
  } else {
    logger.Printf("Sites are %s", sites)
  }

  return C.CString("{}")
}

func loadConfig (path, file string) config.Provider {
  cfg, configFiles, err := hugolib.LoadConfig(hugolib.ConfigSourceDescriptor{Fs: fs, Filename: file, WorkingDir: path, Environment: Env, Path: path, Logger: loggers.NewWarningLogger()})

  for _, f := range configFiles {
    logger.Printf("Loaded file %s", f)
  }

  if err != nil {
    logger.Printf("Error: %s", err.Error())
  }

  cfg.Set("workingDir", path)
  return cfg
}

func findConfig (path string) (string, error)  {
  for _, prefix := range config.DefaultConfigNames {
    for _, suffix := range config.ValidConfigFileExtensions {
      filename := prefix + "." + suffix
      //logger.Printf("Checking for %s in %s", filename, path)
      s, err := afero.Exists(fs, filepath.Join(path, filename))
      if err != nil {
        return "", errors.New("Error: Config file not found")
      }
      if (s) {
        return filename, nil
      }
    }
  }
  return "", errors.New("Error: Config file not found")
}

func cfgToStr(cfg config.Provider) (string) {
  baseConfig := make(map[string]any)
  for _, k := range ConfigDefaults {
    baseConfig[k] = cfg.GetString(k)
  }

  for _, l := range Keys(config.ConfigRootKeysSet) {
    baseConfig[l] = cfg.GetStringMap(l)
  }

  jsonStr, err := json.Marshal(&baseConfig)
  if err != nil {
      logger.Printf("Error: %s", err.Error())
      return "{}"
  } else {
      logger.Println(string(jsonStr))
      return string(jsonStr)
  }
}

/*
//export GetDebug
func getDebug() (C.bool) {
  return C.bool(Debug)
}
*/

//export SetDebug
func SetDebug(debug bool) {
  Debug = debug
  if Debug == true {
    logger.SetOutput(os.Stderr)
  }
}

//export GetEnv
func GetEnv() (*C.char) {
  return C.CString(Env)
}

//export SetEnv
func SetEnv(envPtr *C.char) {
  Env = C.GoString(envPtr)
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
      logger.Fatal(err)
   }
   logger.Println(jsonDocument)
}

func main(){

}
