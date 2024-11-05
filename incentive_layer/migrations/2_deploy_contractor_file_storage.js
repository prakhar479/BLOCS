const ContractorFileStorage = artifacts.require("ContractorFileStorage");

module.exports = function (deployer) {
  // Deploy the ContractorFileStorage contract
  deployer.deploy(ContractorFileStorage);
};