const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");



module.exports = buildModule("ScoreModule", (m) => {


  const scoreContract = m.contract("Score");

//   scoreContract.deployed().then((deployedContract) => {
// 	const envConfig = `CONTRACT_ADDRESS=${deployedContract.address}\n`;
// 	fs.appendFileSync('../../../.env', envConfig);
// 	console.log("Score Contract deployed to:", deployedContract.address);
// });

  return { scoreContract };
});
