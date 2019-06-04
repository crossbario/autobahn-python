///////////////////////////////////////////////////////////////////////////////
//
//  XBR Open Data Markets - https://xbr.network
//
//  JavaScript client library for the XBR Network.
//
//  Copyright (C) Crossbar.io Technologies GmbH and contributors
//
//  Licensed under the Apache 2.0 License:
//  https://opensource.org/licenses/Apache-2.0
//
///////////////////////////////////////////////////////////////////////////////

// https://truffleframework.com/docs/truffle/testing/writing-tests-in-javascript

// let reward = web3.toWei(1, 'ether');
const web3 = require("web3");
const helpers = require("./helpers.js");

const XBRNetwork = artifacts.require("./XBRNetwork.sol");
const XBRToken = artifacts.require("./XBRToken.sol");

console.log('library versions: web3="' + web3.version);



contract('XBRNetwork', accounts => {

    //const gasLimit = 6721975;
    const gasLimit = 0xfffffffffff;
    //const gasLimit = 100000000;

    // deployed instance of XBRNetwork
    var network;

    // deployed instance of XBRNetwork
    var token;

    // https://solidity.readthedocs.io/en/latest/frequently-asked-questions.html#if-i-return-an-enum-i-only-get-integer-values-in-web3-js-how-to-get-the-named-values

    // enum MemberLevel { NULL, ACTIVE, VERIFIED, RETIRED, PENALTY, BLOCKED }
    const MemberLevel_NULL = 0;
    const MemberLevel_ACTIVE = 1;
    const MemberLevel_VERIFIED = 2;
    const MemberLevel_RETIRED = 3;
    const MemberLevel_PENALTY = 4;
    const MemberLevel_BLOCKED = 5;

    // enum DomainStatus { NULL, ACTIVE, CLOSED }
    const DomainStatus_NULL = 0;
    const DomainStatus_ACTIVE = 1;
    const DomainStatus_CLOSED = 2;

    // enum ActorType { NULL, NETWORK, MARKET, PROVIDER, CONSUMER }
    const ActorType_NULL = 0;
    const ActorType_NETWORK = 1;
    const ActorType_MARKET = 2;
    const ActorType_PROVIDER = 3;
    const ActorType_CONSUMER = 4;

    // enum NodeType { NULL, MASTER, CORE, EDGE }
    const NodeType_NULL = 0;
    const NodeType_MASTER = 1;
    const NodeType_CORE = 2;
    const NodeType_EDGE = 3;

    //
    // test accounts setup
    //

    // the XBR Project
    const owner = accounts[0];

    // 2 test XBR market owners
    const alice = accounts[1];
    const alice_market_maker1 = accounts[2];

    const bob = accounts[3];
    const bob_market_maker1 = accounts[4];

    // 2 test XBR data providers
    const charlie = accounts[5];
    const charlie_provider_delegate1 = accounts[6];

    const donald = accounts[7];
    const donald_provider_delegate1 = accounts[8];

    // 2 test XBR data consumers
    const edith = accounts[9];
    const edith_provider_delegate1 = accounts[10];

    const frank = accounts[11];
    const frank_provider_delegate1 = accounts[12];

    beforeEach('setup contract for each test', async function () {
        network = await XBRNetwork.deployed();
        token = await XBRToken.deployed();
    });

    /*
    afterEach(function (done) {
    });
    */

    it('XBRNetwork.createMarket() : should create new market', async () => {

        if (false) {
            const eula = "QmU7Gizbre17x6V2VR1Q2GJEjz6m8S1bXmBtVxS2vmvb81";
            const profile = "QmQMtxYtLQkirCsVmc3YSTFQWXHkwcASMnu5msezGEwHLT";

            await network.register(eula, profile, {from: alice, gasLimit: gasLimit});
        }

        const marketId = web3.utils.sha3("MyMarket1").substring(0, 34);
        const maker = alice_market_maker1;

        const terms = "";
        const meta = "";

        // 100 XBR security
        const providerSecurity = 100 * 10**18;
        const consumerSecurity = 100 * 10**18;

        // 5% market fee
        const marketFee = 0.05 * 10**9 * 10**18

        await network.createMarket(marketId, terms, meta, maker, providerSecurity, consumerSecurity, marketFee, {from: alice, gasLimit: gasLimit});
    });

    it('XBRNetwork.joinMarket() : provider should join existing market', async () => {

        // the XBR provider we use here
        const provider = bob;

        // setup event watching
        console.log('library versions: web3="' + web3.version);
        //const currentBlock = await web3.eth.getBlockNumber();
        const currentBlock = 0;
        var events_ok = false;
        const filter = {};

        let event = network.ActorJoined(filter);

        let watcher = async function (err, result) {
            console.log('XXXXX', result);

            if (true || result.event == 'ActorJoined') {
                // bytes16 marketId, address actor, ActorType actorType, uint256 security

                assert.equal(result.args.marketId, marketId, "wrong marketId in event");
                assert.equal(result.args.actor, provider, "wrong provider address in event");
                assert.equal(result.args.actorType, ActorType_PROVIDER, "wrong actorType in event");
                assert.equal(result.args.security, providerSecurity, "wrong providerSecurity in event");

                events_ok = true;
                event.stopWatching()
                console.log('event watching stopped');
            }
        }


/*
        network.once('ActorJoined', {
            filter: filter,
            fromBlock: currentBlock
        }, function(error, event){ console.log(event); });
*/
/*
        network.events.ActorJoined(
            {
                filter: filter,
                fromBlock: currentBlock
            },
            function (error, event) {
                console.log(event);
            }
        )
        .on('data', function (event) {
            // same results as the optional callback above
            console.log ('event::on_data', event);
        })
        .on('changed', function (event) {
            // remove event from local database
            console.log ('event::on_changed', event);
        })
        .on('error', console.error);
*/
        // 100 XBR security
        const providerSecurity = 100 * 10**18;

        // XBR market to join
        const marketId = web3.utils.sha3("MyMarket1").substring(0, 34);

        // transfer 1000 XBR to provider
        const txn1 = await token.transfer(provider, 1000 * 10**18, {from: owner, gasLimit: gasLimit});
        console.log('1111', txn1);
        await helpers.mine_tx(txn1.tx);

        // XBR provider joins market
        const txn2 = await token.approve(network.address, providerSecurity, {from: provider, gasLimit: gasLimit});
        console.log('2222', txn2);
        await helpers.mine_tx(txn2.tx);

        const txn3 = await network.joinMarket(marketId, ActorType_PROVIDER, {from: provider, gasLimit: gasLimit});
        console.log('3333', txn3);
        await helpers.mine_tx(txn3.tx);

        await awaitEvent(event, watcher);

        //assert.equal(txn_result, providerSecurity, "wrong effective security returned");

        const provider_level = await network.getMemberLevel(provider);
        assert.equal(provider_level.toNumber(), 0, "wrong provider member level");
        //assert.equal(provider_level.toNumber(), MemberLevel_ACTIVE, "wrong provider member level");
/*
        const event = network.ActorJoined(filter, {fromBlock: 0, toBlock: 'latest'}, function (err, result) {
            console.log('XXXXX', result);

            if (true || result.event == 'ActorJoined') {
                // bytes16 marketId, address actor, ActorType actorType, uint256 security

                assert.equal(result.args.marketId, marketId, "wrong marketId in event");
                assert.equal(result.args.actor, provider, "wrong provider address in event");
                assert.equal(result.args.actorType, ActorType_PROVIDER, "wrong actorType in event");
                assert.equal(result.args.security, providerSecurity, "wrong providerSecurity in event");

                events_ok = true;
                event.stopWatching()
                console.log('event watching stopped');
            }

        });
*/
/*
        const event = network.ActorJoined(filter, {fromBlock: 0, toBlock: 'latest'});

        event.watch((err, result) => {

            console.log('XXXXX', result);

            if (true || result.event == 'ActorJoined') {
                // bytes16 marketId, address actor, ActorType actorType, uint256 security

                assert.equal(result.args.marketId, marketId, "wrong marketId in event");
                assert.equal(result.args.actor, provider, "wrong provider address in event");
                assert.equal(result.args.actorType, ActorType_PROVIDER, "wrong actorType in event");
                assert.equal(result.args.security, providerSecurity, "wrong providerSecurity in event");

                events_ok = true;
                event.stopWatching()
                console.log('event watching stopped');
            }
        });
*/
        //assert(events_ok, "event(s) we expected not emitted");
    });

    it('XBRNetwork.joinMarket() : consumer should join existing market', async () => {

        const consumer = charlie;

        // transfer 1000 XBR to consumer
        if (!await token.transfer(consumer, 1000 * 10**18, {from: owner, gasLimit: gasLimit})) {
            throw 'consumer security transfer failed';
        }

        // 100 XBR security
        const consumerSecurity = 100 * 10**18;

        // XBR market to join
        const marketId = web3.utils.sha3("MyMarket1").substring(0, 34);

        // XBR consumer joins market
        if (!await token.approve(network.address, consumerSecurity, {from: consumer, gasLimit: gasLimit})) {
            throw 'consumer security transfer approval failed';
        }
        await network.joinMarket(marketId, ActorType_CONSUMER, {from: consumer, gasLimit: gasLimit});
    });

});
