package br.com.zup.ot6.izabel.proposta.controladores;

import br.com.zup.ot6.izabel.proposta.cartao.ValidadorCartao;
import br.com.zup.ot6.izabel.proposta.dto.PropostaRequest;
import br.com.zup.ot6.izabel.proposta.dto.PropostaResponse;
import br.com.zup.ot6.izabel.proposta.elegibilidade.RetornoElegibilidade;
import br.com.zup.ot6.izabel.proposta.entidades.Proposta;
import br.com.zup.ot6.izabel.proposta.excecoes.PropostaExistenteValidador;
import java.net.URI;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.transaction.Transactional;
import javax.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

@RestController
@Slf4j
public class PropostaControlador {

  @PersistenceContext private EntityManager entityManager;

  @Autowired private PropostaExistenteValidador propostaValidador;

  @Autowired private ValidadorCartao validadorCartao;

  @GetMapping(value = "/proposta/{id}")
  public ResponseEntity<PropostaResponse> acompanharProposta(@PathVariable Long id) {
    Proposta proposta = entityManager.find(Proposta.class, id);
    return proposta != null
        ? ResponseEntity.ok(new PropostaResponse(proposta))
        : ResponseEntity.notFound().build();
  }

  @PostMapping(value = "/proposta")
  @Transactional
  public ResponseEntity<?> cadastrarProposta(@RequestBody @Valid PropostaRequest propostaRequest) {
    Proposta proposta = propostaRequest.converterParaEntidade();
    entityManager.persist(proposta);
    log.info("Proposta {} salva.", proposta);

    RetornoElegibilidade status = validadorCartao.avaliaElegibilidade(proposta);
    log.info("Status de elegibilidade {}", status);
    proposta.setElegibilidade(status.getElegibilidade());
    entityManager.merge(proposta);

    URI location =
        ServletUriComponentsBuilder.fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(proposta.getId())
            .toUri();

    return status.equals(RetornoElegibilidade.COM_RESTRICAO)
        ? ResponseEntity.unprocessableEntity().build()
        : ResponseEntity.created(location).build();
  }

  @InitBinder
  public void initBinder(WebDataBinder binder) {
    binder.addValidators(propostaValidador);
  }
}
