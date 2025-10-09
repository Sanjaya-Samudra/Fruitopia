import { Routes } from '@angular/router';
import { FruitListComponent } from './fruit/fruit-list/fruit-list.component';
import { VisionUploadComponent } from './vision-upload/vision-upload.component';
import { GalleryComponent } from './gallery/gallery.component';
import { RecommendComponent } from './recommend/recommend.component';

export const routes: Routes = [
	{ path: '', component: FruitListComponent },
	{ path: 'vision', component: VisionUploadComponent },
	{ path: 'gallery', component: GalleryComponent },
	{ path: 'recommend', component: RecommendComponent }
];
