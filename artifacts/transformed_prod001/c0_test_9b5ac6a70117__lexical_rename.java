package com.example.application.services;

import com.example.application.models.Product;
import com.example.application.repository.ProductRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

@Service
public class ProductServiceImpl implements ProductService {

    private final ProductRepository productRepository_renamed;

    public ProductServiceImpl(ProductRepository productRepository_renamed) {
        this.productRepository_renamed = productRepository_renamed;
    }

    @Override
    public List<Product> findAll() {
        return StreamSupport.stream(productRepository_renamed.findAll().spliterator(), false).collect(Collectors.toList());
    }

    @Override
    public Long count() {
        return productRepository_renamed.count();
    }

    @Override
    public void delete(Product product) {
        productRepository_renamed.delete(product);
    }

    @Override
    public void save(Product product) {
        productRepository_renamed.save(product);
    }

    @Override
    public Set<Product> getList(List<Product> products) {
        return products.stream().collect(Collectors.toSet());
    }

    @Override
    public Set<Product> getList(String filter) {
        return getList(productRepository_renamed.findByDescriptionContainingIgnoreCase(filter));
    }

    @Override
    public Set<Product> getList(Long id) {
        return getList(productRepository_renamed.findByUserId(id));
    }

    @Override
    public Set<Product> getListCategory(String categoryType) {
        return getList(productRepository_renamed.findByCategoryCategoryType(categoryType));
    }
}
