const ContractorFileStorage = artifacts.require("ContractorFileStorage");

module.exports = function (deployer) {
  deployer.deploy(ContractorFileStorage);
};