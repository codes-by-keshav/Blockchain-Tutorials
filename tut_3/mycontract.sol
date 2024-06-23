// SPDX-License-Identifier: GPL-3.0


pragma solidity >=0.7.0 <0.9.0;

contract Kinkcoin {
    uint64 public max_kinkcoins = 1000000000000000;
    uint public usd_to_kinkcoin = 10;
    uint public total_kinkcoins_bought = 0;

    mapping(address => uint) public equity_kinkcoin;
    mapping(address => uint) public equity_usd;

    modifier can_buy_kinkcoins(uint usd_invested) {
        require(usd_invested * usd_to_kinkcoin + total_kinkcoins_bought <= max_kinkcoins, "Not enough kinkcoin");
        _;
    }

    function equity_in_kinkcoins(address investor) external view returns (uint) {
        return equity_kinkcoin[investor];
    }

    function equity_in_usd(address investor) external view returns (uint) {
        return equity_usd[investor];
    }

    function buy_kinkcoins(address investor, uint usd_invested) external 
    can_buy_kinkcoins(usd_invested){
        uint kinkcoins_bought= usd_invested*usd_to_kinkcoin;
        equity_kinkcoin[investor] += kinkcoins_bought;
        equity_usd[investor]= equity_kinkcoin[investor]/10;
        total_kinkcoins_bought += kinkcoins_bought;
    }

    function sell_kinkcoins(address investor, uint kinkcoins_sold)external{
        equity_kinkcoin[investor] -= kinkcoins_sold;
        equity_usd[investor] = equity_kinkcoin[investor]/10;
        total_kinkcoins_bought -= kinkcoins_sold;
    }

}