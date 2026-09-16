const fs=require('node:fs'),path=require('node:path'),sharp=require('sharp');
const dir=path.join(__dirname,'..','assets');
Promise.all(fs.readdirSync(dir).filter(f=>f.endsWith('.svg')).map(f=>sharp(path.join(dir,f)).png().toFile(path.join(dir,f.replace('.svg','.png'))))).catch(e=>{console.error(e.message);process.exitCode=1;});
