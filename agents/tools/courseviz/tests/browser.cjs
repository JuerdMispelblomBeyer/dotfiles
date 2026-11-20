/* Optional: NODE_PATH=... COURSEVIZ_CHROMIUM=... node tests/browser.cjs GALLERY_DIR */
const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const fs=require('node:fs');
(async()=>{
 const dir=path.resolve(process.argv[2]);
 const browser=await chromium.launch({headless:true,...(process.env.COURSEVIZ_CHROMIUM?{executablePath:process.env.COURSEVIZ_CHROMIUM}:{})});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1080}});
  const failures=[];let count=0;
  for(const file of fs.readdirSync(dir).filter(f=>f.endsWith('.html')&&f!=='index.html')) {
   const errors=[];const onError=e=>errors.push(e.message);page.on('pageerror',onError);
   await page.goto(pathToFileURL(path.join(dir,file)).href);await page.evaluate(()=>document.fonts.ready);
   const result=await page.evaluate(()=>{
    const svg=document.querySelector('.viewport > svg, .frame svg');
    const texts=[...document.querySelectorAll('svg text')];
    const invisible=texts.filter(t=>!t.closest('[hidden]') && (!t.getBoundingClientRect().width || !t.getBoundingClientRect().height)).map(t=>t.textContent);
    const escaped=[...document.querySelectorAll('*')].filter(e=>e.tagName.includes(':')).length;
    return {texts:texts.length,invisible,escaped,svg:!!svg};
   });
   if(!result.svg||!result.texts||result.escaped||result.invisible.length||errors.length)failures.push({file,...result,errors});
   if(await page.locator('#next').count()) {
    await page.locator('#next').click();
    if(!(await page.locator('#position').textContent()).startsWith('2 /'))failures.push({file,error:'step control failed'});
    await page.locator('#all').click();
    if(await page.locator('.frame:visible').count()<2)failures.push({file,error:'show all failed'});
   }
   page.off('pageerror',onError); count++;
  }
  await page.goto(pathToFileURL(path.join(dir,'index.html')).href);
  await page.locator('#filter').fill('unlikely-no-matching-visual');
  if(await page.locator('.card:visible').count())failures.push({error:'gallery filter failed'});
  console.log(JSON.stringify({pages:count,failures},null,2));
  if(failures.length)process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});
