use clap;
use walkdir::WalkDir;
use pbo;
use regex::Regex;
use serde_derive::{Serialize};

use std::ffi::OsStr;
use std::fs::File;
use std::io::Read;
use std::collections::HashMap;

#[derive(Debug, Serialize)]
struct Key {
    original: String,
    english: String,
    czech: String,
    german: String,
    russian: String,
    polish: String,
    italian: String,
    spanish: String,
    french: String,
    chinese: String,
    japanese: String,
    korean: String,
    portuguese: String,
    chinesesimp: String,
    turkish: String,
}

impl Key {
    pub fn new(data: HashMap<String, String>) -> Self {
        Self {
            original: data.get("Original").unwrap().to_string(),
            english: data.get("English").unwrap().to_string(),
            czech: data.get("Czech").unwrap().to_string(),
            german: data.get("German").unwrap().to_string(),
            russian: data.get("Russian").unwrap().to_string(),
            polish: data.get("Polish").unwrap().to_string(),
            italian: data.get("Italian").unwrap().to_string(),
            spanish: data.get("Spanish").unwrap().to_string(),
            french: data.get("French").unwrap().to_string(),
            chinese: data.get("Chinese").unwrap().to_string(),
            japanese: data.get("Japanese").unwrap().to_string(),
            korean: data.get("Korean").unwrap().to_string(),
            portuguese: data.get("Portuguese").unwrap().to_string(),
            chinesesimp: data.get("Chinesesimp").unwrap().to_string(),
            turkish: data.get("Turkish").unwrap().to_string(),
        }
    }
}

#[derive(Debug, Serialize)]
struct Keys {
    keys: HashMap<String, Key>,
}

fn main() {
    let matches = clap::App::new("Arma 3 Stringtables")
        .version(env!("CARGO_PKG_VERSION"))
        .author(env!("CARGO_PKG_AUTHORS"))
        .arg(clap::Arg::with_name("arma3dir")
            .required(true))
        .get_matches();

    let re_key = Regex::new(r#"(?ms)<Key ID="(.+?)">(.+?)</Key>"#).unwrap();
    let re_lang = Regex::new(r"(?ms)<([A-z]+?)>(.+?)</").unwrap();

    let mut keys = Keys { keys: HashMap::new() };

    for entry in WalkDir::new(matches.value_of("arma3dir").unwrap()).into_iter().filter_map(|e| e.ok()) {
        let path = entry.path();
        if path.is_file() && path.extension().unwrap() == OsStr::new("pbo") && path.file_name().unwrap().to_str().unwrap().to_owned().contains("language") {
            println!("{}", path.display());
            let mut file = File::open(path).unwrap();
            let data = pbo::PBO::read(&mut file).unwrap();
            for mut file in data.files.into_iter().filter(|e| e.0.contains("stringtable.xml")) {
                let mut bytes = Vec::new();
                file.1.read_to_end(&mut bytes).unwrap();
                let content = String::from_utf8(bytes).unwrap();
                let result = re_key.captures_iter(&content);
                for mat in result {
                    let languages = re_lang.captures_iter(&mat[2]);
                    let mut map = HashMap::new();
                    for cap in languages {
                        map.insert(cap[1].to_owned(), cap[2].to_owned());
                    }
                    let key = Key::new(map);
                    keys.keys.insert(mat[1].to_owned(), key);
                }
            }
        }
    }

    let output = File::create("strings.cbor").unwrap();
    serde_cbor::to_writer(output, &keys).unwrap();
}
