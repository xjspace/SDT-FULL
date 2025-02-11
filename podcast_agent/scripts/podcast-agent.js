const { processPodcast } = require('../src/podcast-processor');

async function main() {
  try {
    const episodeUrl = process.argv[2];
    if (!episodeUrl) {
      console.error('请提供播客节目URL作为参数');
      process.exit(1);
    }

    console.log('开始处理播客节目:', episodeUrl);
    const result = await processPodcast(episodeUrl);
    console.log('处理完成:');
    console.log(JSON.stringify(result, null, 2));

  } catch (error) {
    console.error('处理过程中发生错误:');
    console.error(error);
    process.exit(1);
  }
}

main();
