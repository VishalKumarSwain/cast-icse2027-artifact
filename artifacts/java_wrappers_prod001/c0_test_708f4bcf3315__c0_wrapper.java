import java.util.*;
import java.io.*;

class PilotWrapper_c0_test_708f4bcf3315 {
public void loadFolder(File folder) {
		LinearLayout root = this.chooser.getRootLayout();
		LinearLayout layout = (LinearLayout) root.findViewById(R.id.linearLayoutFiles);
		layout.removeAllViews();
		if(folder == null || !folder.exists()) {
			if(defaultFolder != null) {
				this.currentFolder = defaultFolder;			
			} else {
				this.currentFolder = Environment.getExternalStorageDirectory();
			}
		} else {
			this.currentFolder = folder;
		}
		if(this.currentFolder.exists() && layout != null) {
			List<FileItem> fileItems = new LinkedList<FileItem>();
			if(this.currentFolder.getParent() != null) {
				File parent = new File(this.currentFolder.getParent());
				if(parent.exists()) {
					fileItems.add(new FileItem(this.chooser.getContext(), parent, ".."));					
				}
			}
			if(this.currentFolder.isDirectory()) {
				File[] fileList = this.currentFolder.listFiles();
				if(fileList != null) {
					Arrays.sort(fileList, new Comparator<File>() {
						public int compare(File file1, File file2) {
							if(file1 != null && file2 != null) {
								if(file1.isDirectory() && (!file2.isDirectory())) return -1;
								if(file2.isDirectory() && (!file1.isDirectory())) return 1;
								return file1.getName().compareTo(file2.getName());
							}
							return 0;
						}
					});		
					for(int i=0; i<fileList.length; i++) {
						boolean selectable = true;
						if(!fileList[i].isDirectory()) {
							selectable = !this.folderMode && (this.filter == null || fileList[i].getName().matches(this.filter));
						}
						if(selectable || !this.showOnlySelectable) {
							FileItem fileItem = new FileItem(this.chooser.getContext(), fileList[i]);
							fileItem.setSelectable(selectable);
							fileItems.add(fileItem);
						}
					}
				}
				String currentFolderName = this.showFullPathInTitle? this.currentFolder.getPath() : this.currentFolder.getName();
				this.chooser.setCurrentFolderName(currentFolderName);
			} else {
				fileItems.add(new FileItem(this.chooser.getContext(), this.currentFolder));
			}
			for(int i=0; i<fileItems.size(); i++) {
				fileItems.get(i).addListener(this.fileItemClickListener);
				layout.addView(fileItems.get(i));
			}
			defaultFolder = this.currentFolder;
		}			
	}
}
