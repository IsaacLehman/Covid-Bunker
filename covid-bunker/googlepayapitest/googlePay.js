//Google pay API functions to use in checkout


//Load pay api
<script async
src="https://pay.google.com/gp/p/js/pay.js"
onload="onGooglePayLoaded()">
</script>

//Specify TEST enviroment
function onGooglePayLoaded(){
    const googlePayClient = 
    new google.payments.api.PaymentsClient({
        enviroment: 'TEST'
    });
}

//Specify client
const clientConfiguration = {
    apiVersion: 2,
    apiVersionMinor: 0,
    allowedPaymentMethods: [VISA]};

//Check if ready to pay and render button
//If on unsupported browser return "error"
googlePayClient.isReadyToPay(clientConfiguration)
    .then(function(response){
        if(response.result){
            googlePayClient.createButton({
                buttonColor:'default',
                buttonType:'long',
                onClick: onGooglePaymentsButtonClicked
            })
        }
    }).catch(function(err){
        console.log("error")
    })

const paymentDataRequest = Object.assign({},
    clientConfiguration);

//Payment Info
paymentDataRequest.transactionInfo = {
    totalPriceStatus:'FINAL',
    totalPrice:'999.99' //Price field here
    currencyCode:'USD'
};

//Merchant Info
paymentDataRequest.merchantInfo = {
    merchantId:'1234567890'
    merchantName:'Admin'
};


//Card/Customer Info
const cardPaymentMethod = {
    type: 'CARD',
    tokenizationSpecification: tokenizationSpec,
    parameters: {
        allowedCardNetworks: ['VISA'],
        allowedAuthMethods: ['PAN_ONLY','CRYPTOGRAM_3DS'],
        billingAddressRequired: true,
        billingAddressParameters: {
            format: 'FULL',
            phoneNumberRequired: true
        }
    }
};

//tokenization specs
const tokenizationSpec = {
    type: 'PAYMENT_GATEWAY',
    parameters: {
        gateway: 'TODO: add gateway',
        gatewayMerchantId: 'merchantGatewayID'
    }
}

//load client payment data and token or return error
googlePayClient.loadPaymentData(paymentDataRequest).then(function(paymentData){
    processPayment(paymentData);
}).catch(function(err){
    console.log("error")
});