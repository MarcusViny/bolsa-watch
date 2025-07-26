import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AtivosModule } from './ativos/ativos.module';

@Module({
  imports: [AtivosModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
