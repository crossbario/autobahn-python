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
        //await main_async(metamask_account);
        //main_cb(metamask_account);
    }
}


const domain = [
    { name: "name", type: "string" },
    { name: "version", type: "string" },
    { name: "chainId", type: "uint256" },
    { name: "verifyingContract", type: "address" },
    { name: "salt", type: "bytes32" },
];

const bid = [
    { name: "amount", type: "uint256" },
    { name: "bidder", type: "Identity" },
];

const identity = [
    { name: "userId", type: "uint256" },
    { name: "wallet", type: "address" },
];

const domainData = {
    name: "XBR",
    version: "1",
    // chainId: parseInt(web3.version.network, 5777),
    chainId: 5777,
    // verifyingContract: "0x1C56346CD2A2Bf3202F771f50d3D14a367B48070",
    salt: "0x3f14acabc1ae39c6b88ba73473141e5f89419cb1285a6b071d5f161cf4c67256"
};

var message = {
    amount: 100,
    bidder: {
        userId: 323,
        wallet: "0x3333333333333333333333333333333333333333"
    }
};

const data = JSON.stringify({
    types: {
        EIP712Domain: domain,
        Bid: bid,
        Identity: identity,
    },
    domain: domainData,
    primaryType: "Bid",
    message: message
});


async function main_async (signer) {
    console.log('testing (async style) with account ' + signer);

    try {
        const result = await web3.currentProvider.sendAsync({
            method: "eth_signTypedData_v3",
            params: [signer, data],
            from: signer
        });

        const signature = result.result.substring(2);
        const r = "0x" + signature.substring(0, 64);
        const s = "0x" + signature.substring(64, 128);
        const v = parseInt(signature.substring(128, 130), 16);

        // The signature is now comprised of r, s, and v.
        console.log('SUCCESS: data successfully signed!');

    } catch (err) {
        console.log('main_async() result: err=', err, 'result=', result);

        if (err.code === -32603) {
            console.log('FAILED: user denied signature!');
        } else {
            console.log('FAILED: signing error', err.code, err.message);
        }
    }
}


function main_cb (signer) {
    console.log('testing (callback style) with account ' + signer);

    web3.currentProvider.sendAsync(
    {
        method: "eth_signTypedData_v3",
        params: [signer, data],
        from: signer
    },

    function (err, result) {
            console.log('main_cb() result: err=', err, 'result=', result);

            // why is that? dunno why error is not delivered in "err", but in result.error
            const error = result.error;

            if (error) {
                if (error.code === -32603) {
                    console.log('FAILED: user denied signature!');
                } else {
                    console.log('FAILED: signing error', error.code, error.message);
                }
            } else {
                const signature = result.result.substring(2);
                const r = "0x" + signature.substring(0, 64);
                const s = "0x" + signature.substring(64, 128);
                const v = parseInt(signature.substring(128, 130), 16);

                console.log('SUCCESS: data successfully signed!');
                console.log('r=' + r);
                console.log('s=' + s);
                console.log('v=' + v);
            }
        }
    );
}


function test_sign_cb () {
    main_cb(metamask_account);
}


async function test_sign_async () {
    await main_async(metamask_account);
}
