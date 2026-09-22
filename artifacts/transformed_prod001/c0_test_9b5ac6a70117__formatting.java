package com.example.application.services;

import com.example.application.models.Product;
import com.example.application.repository.ProductRepository;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.springframework.stereotype.Service;

@Service
public class ProductServiceImpl implements ProductService {

  private final ProductRepository productRepository;

  public ProductServiceImpl(ProductRepository productRepository) {
    this.productRepository = productRepository;
  }

  @Override
  public List<Product> findAll() {
    return StreamSupport.stream(productRepository.findAll().spliterator(), false)
        .collect(Collectors.toList());
  }

  @Override
  public Long count() {
    return productRepository.count();
  }

  @Override
  public void delete(Product product) {
    productRepository.delete(product);
  }

  @Override
  public void save(Product product) {
    productRepository.save(product);
  }

  @Override
  public Set<Product> getList(List<Product> products) {
    return products.stream().collect(Collectors.toSet());
  }

  @Override
  public Set<Product> getList(String filter) {
    return getList(productRepository.findByDescriptionContainingIgnoreCase(filter));
  }

  @Override
  public Set<Product> getList(Long id) {
    return getList(productRepository.findByUserId(id));
  }

  @Override
  public Set<Product> getListCategory(String categoryType) {
    return getList(productRepository.findByCategoryCategoryType(categoryType));
  }
}
