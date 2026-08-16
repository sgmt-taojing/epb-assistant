#!/usr/bin/env node
/**
 * 环保执法案例抓取脚本
 * 用法: node scraper/run.js [options]
 *   --all      抓取全部数据源
 *   --national 仅抓取国家层面
 *   --shandong 仅抓取山东省
 *   --jinan    仅抓取济南市
 *   --limit N  每个数据源最多抓N条（默认50）
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// ============ 配置 ============
const SOURCES_FILE = path.join(__dirname, 'sources.json');
const CASES_FILE   = path.join(__dirname, '..', 'db', 'cases.json');
const LIMIT        = parseInt(process.argv.includes('--limit')
  ? process.argv[process.argv.indexOf('--limit') + 1] || '50' : '50');

// ============ 工具函数 ============
function httpGet(url) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    const req = mod.get(url, { timeout: 15000, headers: { 'User-Agent': 'Mozilla/5.0' } }, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return httpGet(res.headers.location).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) return reject(new Error(`HTTP ${res.statusCode}`));
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
  });
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function extractCases(html, sourceType) {
  // 通用HTML解析：提取处罚公示中的案件信息
  // 匹配模式：标题 + 日期 + 当事人 + 处罚类型
  const results = [];
  
  // 移除注释和script/style标签
  const clean = html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<[^>]+>/g, '|||')
    .replace(/\|\|\|[|\s]+\|\|\|/g, '|||')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#\d+;/g, '');

  // 通用正则：提取列表项（不同页面格式略有差异）
  const lines = clean.split('|||').map(s => s.trim()).filter(Boolean);
  
  let i = 0;
  let batch = [];
  while (i < lines.length && results.length < LIMIT) {
    const line = lines[i];
    // 日期格式: YYYY-MM-DD 或 YYYY/MM/DD
    const dateMatch = line.match(/(20\d{2}[-/年]\d{1,2}[-/月]\d{1,2})/);
    // 关键词过滤: 只要含环保/处罚/行政处罚/罚款/环境违法
    const hasEnv = /[环环保处罚罚款违法行政决定书责令]/.test(line);
    if (dateMatch && hasEnv && line.length > 10 && line.length < 500) {
      batch.push(line);
      if (batch.length >= 3) {
        const type = detectType(batch.join(' '));
        results.push({
          id: `AUTO-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${String(results.length+1).padStart(3,'0')}`,
          date: normalizeDate(dateMatch[1]),
          title: batch[0].slice(0, 120),
          party: extractParty(batch.join(' ')),
          type,
          source: sourceType,
          fact: batch.slice(1).join('；').slice(0, 300),
          law: inferLaws(batch.join(' ')),
          result: '',
          status: 'new',
          tags: extractTags(batch.join(' ')),
          fetchedAt: new Date().toISOString()
        });
        batch = [];
      }
    }
    i++;
  }

  return results;
}

function normalizeDate(str) {
  return str.replace(/年/g,'-').replace(/月/g,'-').replace(/\//g,'-').replace(/--/g,'-');
}

function detectType(text) {
  if (/危[险废料固体废物]|固体废物|危废/.test(text)) return '固体废物污染类';
  if (/超标排放|大气|废气|VOC|烟尘|粉尘/.test(text)) return '大气污染类';
  if (/水|废水|排污|暗管|渗坑|超标/.test(text)) return '水污染类';
  if (/噪声|噪音|扰民/.test(text)) return '噪声污染类';
  if (/土壤|重金属/.test(text)) return '土壤污染类';
  if (/环评|未批先建|批建不符|未验先投/.test(text)) return '环评类';
  if (/无证|排污许可|超许可/.test(text)) return '排污许可类';
  if (/在线监测|数据造假|监控/.test(text)) return '自动监控类';
  if (/辐射|射线|放射/.test(text)) return '辐射污染类';
  if (/生态|自然保护|破坏/.test(text)) return '生态破坏类';
  return '其他类';
}

function extractParty(text) {
  const m = text.match(/当事人[：:]*\s*([^\s，,。]{2,30}?)(?:公司|厂| 企业| 单位| 个人| 户|$)/);
  if (m) return m[1];
  const m2 = text.match(/被处罚人[：:]*\s*([^\s，,。]{2,30}?)(?:公司|厂| 企业| 单位| 个人| 户|$)/);
  if (m2) return m2[1];
  const m3 = text.match(/(?:^|[^\\u4e00-\\u9fa5])([^\s，,。]{5,20}(?:公司|厂|企业|中心|集团|合作社))/);
  if (m3) return m3[1];
  return '未查明';
}

function inferLaws(text) {
  const laws = [];
  if (/超标排放|大气/.test(text)) laws.push('《大气污染防治法》第99条');
  if (/水|废水|排污/.test(text)) laws.push('《水污染防治法》第83条');
  if (/危废|固体废物/.test(text)) laws.push('《固体废物污染环境防治法》第112条');
  if (/未批先建/.test(text)) laws.push('《环境影响评价法》第31条');
  if (/未验先投/.test(text)) laws.push('《建设项目环境保护管理条例》第23条');
  if (/无证排污/.test(text)) laws.push('《排污许可管理条例》第33条');
  if (/在线监测|数据造假/.test(text)) laws.push('《刑法》第286条之一（破坏计算机信息系统罪）');
  if (/噪声/.test(text)) laws.push('《噪声污染防治法》第62条');
  return laws.length ? laws : ['相关环保法律法规'];
}

function extractTags(text) {
  const tags = [];
  if (/罚款|处罚/.test(text)) tags.push('罚款');
  if (/责令|限期/.test(text)) tags.push('责令整改');
  if (/停产|停业/.test(text)) tags.push('停产停业');
  if (/刑事|拘留|判刑/.test(text)) tags.push('刑事移送');
  if (/查封|扣押/.test(text)) tags.push('行政强制');
  if (/按日连续/.test(text)) tags.push('按日计罚');
  return tags;
}

function loadCases() {
  if (!fs.existsSync(CASES_FILE)) return [];
  try { 
    const data = JSON.parse(fs.readFileSync(CASES_FILE, 'utf8'));
    return Array.isArray(data) ? data : (data.cases || []);
  }
  catch { return []; }
}

function saveCases(cases) {
  const dir = path.dirname(CASES_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(CASES_FILE, JSON.stringify(cases, null, 2), 'utf8');
}

// ============ 抓取单个数据源 ============
async function scrapeSource(source) {
  console.log(`\n📡 正在抓取: ${source.name} (${source.url})`);
  try {
    const html = await httpGet(source.url);
    const cases = extractCases(html, source.name);
    if (cases.length === 0) {
      console.log(`  ⚠️  未解析到案例（可能页面结构不同，需手动适配）`);
      return [];
    }
    console.log(`  ✅ 解析到 ${cases.length} 条案例`);
    return cases;
  } catch (e) {
    console.log(`  ❌ 抓取失败: ${e.message}`);
    return [];
  }
}

// ============ 主程序 ============
async function main() {
  const args = process.argv.slice(2);
  const sources = JSON.parse(fs.readFileSync(SOURCES_FILE, 'utf8')).sources;

  // 过滤数据源
  let targets = sources;
  if (args.includes('--national')) targets = targets.filter(s => s.type === 'national');
  else if (args.includes('--shandong') || args.includes('--province')) targets = targets.filter(s => s.type === 'provincial');
  else if (args.includes('--jinan') || args.includes('--city')) targets = targets.filter(s => s.type === 'city');
  else if (args.includes('--credit')) targets = targets.filter(s => s.type === 'credit');

  console.log('========================================');
  console.log('🌿 环保执法案例抓取工具 v1.0');
  console.log('========================================');
  console.log(`目标数据源: ${targets.map(s => s.name).join(', ')}`);
  console.log(`每源最大条数: ${LIMIT}`);
  console.log('');

  const allNewCases = [];
  for (const src of targets) {
    const cases = await scrapeSource(src);
    if (cases.length > 0) allNewCases.push(...cases);
    await sleep(2000); // 礼貌爬取，避免被封
  }

  // 合并去重（按日期+当事人+类型）
  const existing = loadCases();
  const existingKeys = new Set(existing.map(c => `${c.date}|${c.party}|${c.type}`));
  const newOnly = allNewCases.filter(nc => !existingKeys.has(`${nc.date}|${nc.party}|${nc.type}`));
  
  const updated = [...newOnly, ...existing].slice(0, 2000); // 最多保留2000条

  saveCases(updated);

  console.log('');
  console.log('========================================');
  console.log('📊 抓取完成报告');
  console.log('========================================');
  console.log(`新增案例: ${newOnly.length} 条`);
  console.log(`总收录:    ${updated.length} 条`);
  console.log(`保存位置:  ${CASES_FILE}`);

  if (newOnly.length > 0) {
    console.log('');
    console.log('📌 最新收录:');
    newOnly.slice(0, 5).forEach(c => {
      console.log(`  [${c.id}] ${c.date} | ${c.party} | ${c.type}`);
      console.log(`    ${c.title}`);
    });
  }
}

main().catch(e => { console.error('Fatal:', e); process.exit(1); });
