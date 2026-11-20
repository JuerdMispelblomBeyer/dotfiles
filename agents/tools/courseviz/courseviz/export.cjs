/* Optional raster/print adapter. No remote requests, CDN, or embedded credentials. */
const {pathToFileURL}=require('node:url');
(async()=>{
 const {chromium}=require('playwright');
 const [input,output,width,scale]=process.argv.slice(2);
 const browser=await chromium.launch({headless:true,...(process.env.COURSEVIZ_CHROMIUM ? {executablePath:process.env.COURSEVIZ_CHROMIUM} : {})});
 try {
  const page=await browser.newPage({viewport:{width:Number(width),height:900},deviceScaleFactor:Number(scale),reducedMotion:'reduce'});
  await page.route('**/*',route=>route.request().url().startsWith('file:')||route.request().url().startsWith('data:')?route.continue():route.abort());
  await page.goto(pathToFileURL(input).href,{waitUntil:'load'});
  await page.evaluate(async()=>{await document.fonts.ready;document.querySelectorAll('.frame').forEach(f=>f.hidden=false);document.querySelectorAll('nav').forEach(n=>n.style.display='none')});
  if(output.toLowerCase().endsWith('.pdf')) await page.pdf({path:output,format:'A3',printBackground:true,margin:{top:'12mm',bottom:'12mm',left:'12mm',right:'12mm'}});
  else await page.locator('.viewport').screenshot({path:output,animations:'disabled'});
 } finally {await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});
