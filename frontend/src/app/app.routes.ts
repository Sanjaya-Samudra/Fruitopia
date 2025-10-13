import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { FruitListComponent } from './fruit/fruit-list/fruit-list.component';
import { VisionUploadComponent } from './vision-upload/vision-upload.component';
import { GalleryComponent } from './gallery/gallery.component';
import { ExploreComponent } from './explore/explore.component';
import { RecommendComponent } from './recommend/recommend.component';
import { RecipeComponent } from './recipe/recipe.component';
import { ChatWidgetComponent } from './chat-widget/chat-widget.component';

export const routes: Routes = [
	{ path: '', component: HomeComponent },
	{ path: 'fruits', component: FruitListComponent },
	{ path: 'vision', component: VisionUploadComponent },
	{ path: 'gallery', component: GalleryComponent },
	{ path: 'explore/:name', component: ExploreComponent },
	{ path: 'recommend', component: RecommendComponent },
	{ path: 'recipes', component: RecipeComponent },
	{ path: 'chat', component: ChatWidgetComponent }
];
