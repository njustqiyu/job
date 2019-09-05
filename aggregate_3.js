/*将配置的yml文件转换为同名的json文件存取*/
let yaml = require('js-yaml');
let fs = require('fs');
let path = require('path');
let filePath = "./config/ruleConfig/rulesConfig.yml";
let data;
try {
    data = yaml.safeLoad(fs.readFileSync(filePath, 'utf8'));
}
catch (e) {
    console.log(e);
}
fs.writeFile(path.join('./config/ruleConfig/rulesConfig.json'), JSON.stringify(data), function (err) {
    if (err){
        throw err;
    }
    console.log("Export yaml2json(rulesConfig.yml) success!");
});

