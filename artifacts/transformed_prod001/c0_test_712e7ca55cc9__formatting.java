import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class MyItemServiceImpl implements MyItemServiceInterface {

  @Autowired private MyItemRepository myItemRepository;

  @Override
  public void saveItem(MyItem item) {
    myItemRepository.save(item);
  }

  @Override
  public MyItem findByItemName(String name) {
    return myItemRepository.findByName(name);
  }

  @Override
  public List<MyItem> findItems() {
    return myItemRepository.findAll();
  }
}
