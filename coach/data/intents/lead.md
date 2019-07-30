## intent:i_wanna_buy
- quero [comprar](trading_type) um [apartamento](property_type)
- Quero [comprar](trading_type) uma [casa](property_type)
- gostaria de [comprar](trading_type) um [ap](property_type:apartamento)
- desejo [comprar](trading_type) um [terreno](property_type)
- gostaria de [comprar](trading_type) um [apartamento](property_type)
- tenho interesse em [comprar](trading_type) uma [casa](property_type)
- pretendo [compra](trading_type:comprar) um [ap](property_type:apartamento)
- eu pretendo [mercar](trading_type:comprar) um [apartamento](property_type)
- intento [obter](trading_type:comprar) um [terreno](property_type)
- gostaria de [adquirir](trading_type:comprar) [comércio](property_type)
- cobiço [compra](trading_type:comprar) de um [comercio](property_type)
- almejo [obter](trading_type:comprar) um [comércio](property_type)
- me interesso em [obter](trading_type:comprar) uma [loja](property_type:comercio)
- quero [adquirir](trading_type:comprar) um imóvel
- tenho interesse em [comprar](trading_type) um imóvel
- quero [comprar](trading_type) um imóvel

## intent:i_wanna_sell
- quero [vender](trading_type) uma [casa](property_type)
- [vender](trading_type) um [apartamento](property_type)
- como faço para [vender](trading_type) uma [casa](property_type)
- [venda](trading_type:vender) um [terreno](property_type)
- Quero [venda](trading_type:vender) um [apartamento](property_type)
- almejo [vender](trading_type:vender) uma [comércio](property_type)
- gostaria de [alienar](trading_type:vender) um [ap](property_type:apartamento)
- desejo [comercializar](trading_type:vender) um [terreno](property_type)
- gostaria de [comerciar](trading_type:vender) uma [casa](property_type)
- tenho interesse em [mercadejar](trading_type:vender) um [apartamento](property_type)
- pretendo [mercantilizar](trading_type:vender) um [ap](property_type:apartamento)
- eu pretendo [mercar](trading_type:vender) um [terreno](property_type)
- intento [mercar](trading_type:vender) uma [loja](property_type:comercio)
- gostaria de [negociar](trading_type:vender) [apartamento](property_type)
- cobiço [transacionar](trading_type:vender) de um [comercio](property_type)

## intent:i_wanna_rent
- quero [alugar](trading_type) uma [casa](property_type)
- [alugar](trading_type) um [lote](property_type:terreno)
- como faço para [alugar](trading_type) uma [loja](property_type:comercio)
- Quero [alugar](trading_type) um [apartamento](property_type)
- almejo [alugar](trading_type) uma [loja](property_type:comercio)
- eu pretendo [alugar](trading_type) um [terreno](property_type)
- intento [alugar](trading_type) um [comercio](property_type)
- gostaria de [alugar](trading_type) [apartamento](property_type)
- cobiço [alugar](trading_type) de um [comercio](property_type)
- [aluga](trading_type:alugar) um [ap](property_type:apartamento)
- gostaria de [locar](trading_type:alugar) um [estabelecimento](property_type:comercio)
- desejo [locar](trading_type:alugar) um [terreno](property_type)
- gostaria de [locar](trading_type:alugar) uma [casa](property_type)
- tenho interesse em [locar](trading_type:alugar) um [apartamento](property_type)
- pretendo [locar](trading_type:alugar) um [ap](property_type:apartamento)

## synonym:comprar
- adquirir
- mercar
- obter
- compra

## synonym:vender
- venda
- alienar
- comercializar
- comerciar
- mercadejar
- mercanciar
- mercantilizar
- mercar
- negociar
- transacionar

## synonym:alugar
- aluga
- locar

## intent:inform_data
- meu cep é [19044-105](zip_code)
- o CEP é [35702-433](zip_code)
- [65076645](zip_code) é o cep
- cep que gostaria eh [77423-505](zip_code)
- [49088-255](zip_code)
- [50791-462](zip_code)
- [76828-510](zip_code)
- [23830-330](zip_code)
- [59604-250](zip_code)
- [66640-696](zip_code)
- [64004-620](zip_code)
- [75528-269](zip_code)
- [58073-444](zip_code)
- [73805-690](zip_code)
- [49042-550](zip_code)
- [13456580](zip_code)
- [58401562](zip_code)
- [82900520](zip_code)
- [76874096](zip_code)
- [40279560](zip_code)
- [87200061](zip_code)
- [86812763](zip_code)
- [88047470](zip_code)
- [76873 386](zip_code)
- [65055 278](zip_code)
- [69303 485](zip_code)
- [37002 140](zip_code)
- [89163 360](zip_code)
- [76914 730](zip_code)
- [78058 024](zip_code)
- [89260 675](zip_code)

## regex:zip_code
- \b[\d]{5}([\d]{3}|-[\d]{3}|\s[\d]{3})\b