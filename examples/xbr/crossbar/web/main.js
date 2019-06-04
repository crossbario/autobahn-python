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

////////////////////

// the XBR Project
window.addr_owner = '0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1';

// 2 test XBR market owners
window.addr_alice = '0xffcf8fdee72ac11b5c542428b35eef5769c409f0';
window.addr_alice_market_maker1 = '0x22d491bde2303f2f43325b2108d26f1eaba1e32b';

window.addr_bob = '0xe11ba2b4d45eaed5996cd0823791e0c93114882d';
window.addr_bob_market_maker1 = '0xd03ea8624c8c5987235048901fb614fdca89b117';

// 2 test XBR data providers
window.addr_charlie = '0x95ced938f7991cd0dfcb48f0a06a40fa1af46ebc';
window.addr_charlie_provider_delegate1 = '0x3e5e9111ae8eb78fe1cc3bb8915d5d461f3ef9a9';

window.addr_donald = '0x28a8746e75304c0780e011bed21c72cd78cd535e';
window.addr_donald_provider_delegate1 = '0xaca94ef8bd5ffee41947b4585a84bda5a3d3da6e';

// 2 test XBR data consumers
window.addr_edith = '0x1df62f291b2e969fb0849d99d9ce41e2f137006e'
window.addr_edith_provider_delegate1 = '0x610bb1573d1046fcb8a70bbbd395754cd57c2b60';

window.addr_frank = '0x855fa758c77d68a04990e992aa4dcdef899f654a';
window.addr_frank_provider_delegate1 = '0xfa2435eacf10ca62ae6787ba2fb044f8733ee843';

////////////////////

var metamask_account = null;
var metamask_network = null;


// demo app entry point
window.addEventListener('load', function () {
    unlock_metamask();
});


// check for MetaMask and ask user to grant access to accounts ..
// https://medium.com/metamask/https-medium-com-metamask-breaking-change-injecting-web3-7722797916a8
// web3.currentProvider.isMetaMask
async function unlock_metamask () {
    if (window.ethereum) {
            // if we have MetaMask, ask user for access
        await ethereum.enable();

        // instantiate Web3 from MetaMask as provider
        //window.web3 = new Web3(window.ethereum);
        window.web3 = new Web3(window.ethereum);
        console.log('ok, user granted access to MetaMask accounts');

        web3.currentProvider.publicConfigStore.on('update', on_metamask_changed);

        // set new provider on XBR library
        xbr.setProvider(window.web3.currentProvider);
        console.log('library versions: web3="' + window.web3.version.api + '", xbr="' + xbr.version + '"');

    } else {
        // no MetaMask (or other modern Ethereum integrated browser) .. redirect
        var win = window.open('https://metamask.io/', '_blank');
        if (win) {
            win.focus();
        }
    }
}


function on_metamask_changed (changed) {
    if (metamask_account != changed.selectedAddress || metamask_network != changed.networkVersion) {
        metamask_account = changed.selectedAddress;
        metamask_network = changed.networkVersion;
        console.log('user switched account to ' + metamask_account + ' on network ' + changed.networkVersion);

        // now setup testing from the accounts ..
        setup_test(metamask_account);
    }
}


// setup test
async function setup_test (account) {
    console.log('setup testing for account ' + account);

    // display addresses of XBR smart contract instances
    document.getElementById('account').innerHTML = '' + account;
    document.getElementById('xbr_network_address').innerHTML = '' + xbr.xbrNetwork.address;
    document.getElementById('xbr_token_address').innerHTML = '' + xbr.xbrToken.address;

    // set main account as default in form elements
    document.getElementById('new_member_address').value = '' + account;
    document.getElementById('get_member_address').value = '' + account;
    document.getElementById('get_market_actor_address').value = '' + account;
    document.getElementById('get_market_owner').value = '' + account;
    document.getElementById('join_market_owner').value = '' + account;
    document.getElementById('get_market_actor_market_owner').value = '' + account;
    document.getElementById('open_channel_market_owner').value = '' + account;
    document.getElementById('new_market_maker_address').value = '' + account;
}


async function test_get_member () {
    var get_member_address = document.getElementById('get_member_address').value;

    // ask for current balance in XBR
    var balance = await xbr.xbrToken.balanceOf(get_member_address);
    if (balance > 0) {
        balance = balance / 10**18;
        console.log('account holds ' + balance + ' XBR');
    } else {
        console.log('account does not hold XBR currently');
    }

    // ask for XBR network membership level
    const level = await xbr.xbrNetwork.getMemberLevel(get_member_address);
    if (level > 0) {
        console.log('account is already member in the XBR network (level=' + level + ')');
        const eula = await xbr.xbrNetwork.getMemberEula(get_member_address);
        const profile = await xbr.xbrNetwork.getMemberProfile(get_member_address);
        console.log('eula:', eula);
        console.log('profile:', profile);
    } else {
        console.log('account is not yet member in the XBR network');
    }
}


async function test_register () {
    const new_member_address = document.getElementById('new_member_address').value;
    const new_member_eula = document.getElementById('new_member_eula').value;
    const new_member_profile = document.getElementById('new_member_profile').value;

    console.log('test_register(new_member_address=' + new_member_address + ', new_member_eula=' + new_member_eula + ', new_member_profile=' + new_member_profile + ')');

    // bytes32 eula, bytes32 profile
    await xbr.xbrNetwork.register(new_member_eula, new_member_profile, {from: metamask_account});
}


async function test_create_market () {
    const decimals = parseInt('' + await xbr.xbrToken.decimals())

    var name = document.getElementById('new_market_name').value;
    var terms = document.getElementById('new_market_terms').value;
    var meta = document.getElementById('new_market_meta').value;
    var maker = document.getElementById('new_market_maker_address').value;
    var providerSecurity = document.getElementById('new_market_provider_security').value;
    var consumerSecurity = document.getElementById('new_market_consumer_security').value;
    var marketFee = document.getElementById('new_market_fee').value;

    providerSecurity = providerSecurity * (10 ** decimals);
    consumerSecurity = consumerSecurity * (10 ** decimals);
    marketFee = marketFee * (10 ** decimals);

    var marketId = web3.sha3((account, name));

    console.log('test_create_market(marketId=' + marketId + ', maker=' + maker + ', terms=' + terms + ', providerSecurity=' + providerSecurity + ', consumerSecurity=' + consumerSecurity + ', marketFee=' + marketFee + ')');

    // bytes32 marketId, address maker, bytes32 terms, uint providerSecurity, uint consumerSecurity
    await xbr.xbrNetwork.createMarket(marketId, terms, meta, maker, providerSecurity, consumerSecurity, marketFee, {from: metamask_account});
}


async function test_get_market () {
    const totalSupply = parseInt('' + await xbr.xbrToken.totalSupply())
    const decimals = parseInt('' + await xbr.xbrToken.decimals())

    var name = document.getElementById('get_market_name').value;
    var owner = document.getElementById('get_market_owner').value;

    var marketId = web3.sha3((owner, name));

    console.log('test_get_market(marketId=' + marketId + ')');

    owner = await xbr.xbrNetwork.getMarketOwner(marketId);
    var terms = await xbr.xbrNetwork.getMarketTerms(marketId);
    var meta = await xbr.xbrNetwork.getMarketMeta(marketId);
    var maker = await xbr.xbrNetwork.getMarketMaker(marketId);
    var providerSecurity = await xbr.xbrNetwork.getMarketProviderSecurity(marketId);
    var consumerSecurity = await xbr.xbrNetwork.getMarketConsumerSecurity(marketId);
    var marketFee = await xbr.xbrNetwork.getMarketFee(marketId);

    providerSecurity = providerSecurity / (10 ** decimals);
    consumerSecurity = consumerSecurity / (10 ** decimals);
    marketFee = marketFee / totalSupply;

    console.log('market ' + marketId + ' owner:', owner);
    console.log('market ' + marketId + ' terms:', terms);
    console.log('market ' + marketId + ' meta:', meta);
    console.log('market ' + marketId + ' maker:', maker);
    console.log('market ' + marketId + ' providerSecurity:', providerSecurity);
    console.log('market ' + marketId + ' consumerSecurity:', consumerSecurity);
    console.log('market ' + marketId + ' marketFee:', marketFee);
}


async function test_join_market () {
    var name = document.getElementById('join_market_name').value;
    var owner = document.getElementById('join_market_owner').value;

    var marketId = web3.sha3((owner, name));

    var actorType = xbr.ActorType.NONE;
    if (document.getElementById('join_market_actor_type_provider').checked) {
        actorType = xbr.ActorType.PROVIDER;
    }
    else if (document.getElementById('join_market_actor_type_consumer').checked) {
        actorType = xbr.ActorType.CONSUMER;
    }
    else {
        assert(false);
    }

    console.log('test_join_market(marketId=' + marketId + ', actorType=' + actorType + ')');

    // bytes32 marketId, ActorType actorType
    await xbr.xbrNetwork.joinMarket(marketId, actorType, {from: metamask_account, gas: 1000000});
}


async function test_get_market_actor_type () {
    var name = document.getElementById('get_market_actor_market_name').value;
    var owner = document.getElementById('get_market_actor_market_owner').value;

    var marketId = web3.sha3((owner, name));

    var actor = document.getElementById('get_market_actor_address').value;

    // bytes32 marketId, address actor
    const actorType = await xbr.xbrNetwork.getMarketActorType(marketId, actor);

    if (actorType > 0) {
        if (actorType == xbr.ActorType.CONSUMER) {
            console.log('account is CONSUMER actor in this market');
        } else if (actorType == xbr.ActorType.PROVIDER) {
            console.log('account is PROVIDER actor in this market');
        } else if (actorType == xbr.ActorType.MAKER) {
            console.log('account is MARKET actor in this market');
        } else if (actorType == xbr.ActorType.NETWORK) {
            console.log('account is NETWORK actor in this market');
        } else {
            console.log('unexpected actor type:', actorType);
        }
    } else {
        console.log('account is not an actor in this market');
    }
}


async function test_open_payment_channel () {
    var name = document.getElementById('open_channel_market_name').value;
    var owner = document.getElementById('open_channel_market_owner').value;

    var marketId = web3.sha3((owner, name));

    var consumer = document.getElementById('open_channel_consumer_address').value;

    const decimals = parseInt('' + await xbr.xbrToken.decimals())
    var amount = document.getElementById('open_channel_amount').value;
    amount = amount * (10 ** decimals);

    const success = await xbr.xbrToken.approve(xbr.xbrNetwork.address, amount, {from: metamask_account});

    if (!success) {
        throw 'transfer was not approved';
    }

    var watch = {
        tx: null
    }

    const options = {};
    xbr.xbrNetwork.PaymentChannelCreated(options, function (error, event)
        {
            console.log('PaymentChannelCreated', event);
            if (event) {
                if (watch.tx && event.transactionHash == watch.tx) {
                    console.log('new payment channel created: marketId=' + event.args.marketId + ', channel=' + event.args.channel + '');
                }
            }
            else {
                console.error(error);
            }
        }
    );

    console.log('test_open_payment_channel(marketId=' + marketId + ', consumer=' + consumer + ', amount=' + amount + ')');

    // bytes32 marketId, address consumer, uint256 amount
    const tx = await xbr.xbrNetwork.openPaymentChannel(marketId, consumer, amount, {from: metamask_account});

    console.log(tx);

    watch.tx = tx.tx;

    console.log('transaction completed: tx=' + tx.tx + ', gasUsed=' + tx.receipt.gasUsed);
}


async function test_get_payment_channel () {
    const channelAddress = document.getElementById('get_channel_channel_address').value;

    channel = xbr.XBRPaymentChannel.at(channelAddress);

    console.log(channel);

    const marketId = await channel.marketId();
    const sender = await channel.sender();
    const delegate = await channel.delegate();
    const recipient = await channel.recipient();
    const amount = await channel.amount();
    const openedAt = await channel.openedAt();
    const closedAt = await channel.closedAt();
    const channelTimeout = await channel.channelTimeout();

    console.log('marketId=' + marketId);
    console.log('sender=' + sender);
    console.log('delegate=' + delegate);
    console.log('recipient=' + recipient);
    console.log('amount=' + amount);
    console.log('openedAt=' + openedAt);
    console.log('closedAt=' + closedAt);
    console.log('channelTimeout=' + channelTimeout);
}


async function test_close_payment_channel () {
    // https://github.com/ethereum/wiki/wiki/JavaScript-API#web3ethsign
}


async function test_request_paying_channel () {

}
