import { of } from 'rxjs';
import { ChatWidgetComponent } from './chat-widget.component';
import { FruitopiaApiService } from '../fruit/fruitopia-api.service';
import { ChatService } from '../services/chat.service';

describe('ChatWidgetComponent', () => {
  let component: ChatWidgetComponent;
  let chatServiceSpy: jasmine.SpyObj<ChatService>;
  let apiServiceSpy: jasmine.SpyObj<FruitopiaApiService>;

  beforeEach(() => {
    chatServiceSpy = jasmine.createSpyObj<ChatService>('ChatService', ['toggleChat', 'openChat', 'closeChat'], {
      chatOpen$: of(false),
      isChatOpen: false,
    });
    apiServiceSpy = jasmine.createSpyObj<FruitopiaApiService>('FruitopiaApiService', ['chatbotMessage']);

    component = new ChatWidgetComponent(apiServiceSpy, chatServiceSpy);
  });

  it('should close chat via the shared chat service', () => {
    component.isOpen = true;
    component.isMinimized = true;
    spyOn<any>(component, 'saveChatHistory');

    component.closeChat();

    expect(chatServiceSpy.closeChat).toHaveBeenCalled();
    expect(component.isOpen).toBeFalse();
    expect(component.isMinimized).toBeFalse();
  });
});
